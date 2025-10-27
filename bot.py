import os
import asyncio
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import httpx
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔑 Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY")
DEFAULT_VOICE = os.environ.get("VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
MODEL_ID = os.environ.get("MODEL_ID", "eleven_multilingual_v2")

chat_voice_map = {}
ELEVEN_BASE = "https://api.elevenlabs.io/v1/text-to-speech"


# 🟢 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Send me some text and I’ll reply with speech.\n"
        "Use /voice <voice_id> to change the voice for this chat.\n\n"
        "Example: /voice 21m00Tcm4TlvDq8ikWAM"
    )


# 🎙️ Change voice per chat
async def set_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args
    if not args:
        current = chat_voice_map.get(chat_id, DEFAULT_VOICE)
        await update.message.reply_text(f"Usage: /voice <voice_id>\nCurrent: {current}")
        return

    voice_id = args[0].strip()
    chat_voice_map[chat_id] = voice_id
    await update.message.reply_text(f"✅ Voice set to: {voice_id}")


# 🧠 ElevenLabs API call
async def tts_text(text: str, voice_id: str):
    url = f"{ELEVEN_BASE}/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_API_KEY,
    }
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.75},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            return resp.content
        else:
            raise RuntimeError(f"ElevenLabs error {resp.status_code}: {resp.text}")


# 💬 Handle incoming text
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    if not text or not text.strip():
        return

    voice_id = chat_voice_map.get(chat_id, DEFAULT_VOICE)
    msg = await update.message.reply_text("🎧 Generating speech...")

    try:
        audio_bytes = await tts_text(text, voice_id)
    except Exception as e:
        await msg.edit_text(f"❌ Error generating speech: {e}")
        return

    # Save and send audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpf:
        tmpf.write(audio_bytes)
        tmp_path = tmpf.name

    try:
        await update.message.reply_audio(
            audio=InputFile(tmp_path), caption="Here you go 🔊"
        )
        await msg.delete()
    finally:
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass


# 🚀 Main bot launcher
async def main():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN missing in environment.")
        return
    if not ELEVEN_API_KEY:
        print("❌ ELEVEN_API_KEY missing in environment.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("voice", set_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot started and polling...")
    await app.run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped manually")

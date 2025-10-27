import os
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =============== ENV VARIABLES ===============
BOT_TOKEN = os.getenv("BOT_TOKEN")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # default ElevenLabs voice

# =============== COMMAND HANDLERS ===============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙️ *Welcome to Voice Bot!*\n\n"
        "Send me any text and I'll reply with speech.\n"
        "Use /voice <voice_id> to set a custom ElevenLabs voice.\n\n"
        "_Powered by ElevenLabs & Telegram Bot API._",
        parse_mode="Markdown",
    )

async def set_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global VOICE_ID
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a voice ID. Example:\n/voice pNInz6obpgDQGcFmaJgB")
        return
    VOICE_ID = context.args[0]
    await update.message.reply_text(f"✅ Voice ID updated to: `{VOICE_ID}`", parse_mode="Markdown")

# =============== MAIN MESSAGE HANDLER ===============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        await update.message.reply_text("⚠️ Please send text only.")
        return

    await update.message.reply_text("🎧 Generating speech, please wait...")

    try:
        # ElevenLabs API call
        async with aiohttp.ClientSession() as session:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
            headers = {
                "xi-api-key": ELEVEN_API_KEY,
                "Content-Type": "application/json",
            }
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.3, "similarity_boost": 0.8},
            }

            async with session.post(url, json=data, headers=headers) as response:
                if response.status != 200:
                    error = await response.text()
                    await update.message.reply_text(f"❌ ElevenLabs API error:\n{error}")
                    return

                audio = await response.read()

        # Save and send voice
        audio_path = "voice.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio)

        await update.message.reply_voice(voice=open(audio_path, "rb"))
        os.remove(audio_path)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

# =============== MAIN APP LOOP ===============
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("voice", set_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot started and polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()  # keep running forever

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

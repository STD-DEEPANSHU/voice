import os
import asyncio
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 🎙️ ElevenLabs Text-to-Speech
def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.85,
            "style": 0.4,
            "use_speaker_boost": True,
            "speed": 0.95  # 👈 slower speech
        },
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

    file_path = "voice.mp3"
    with open(file_path, "wb") as f:
        f.write(response.content)

    return file_path


# 🧠 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Use /voice <text> to generate voice.")


# 🗣️ /voice command
async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("💬 Usage: `/voice your text here`", parse_mode="Markdown")
        return

    text = " ".join(context.args)
    user = update.message.from_user.first_name
    logger.info(f"{user} requested voice for: {text}")

    try:
        file_path = text_to_speech(text)
        await update.message.reply_voice(voice=open(file_path, "rb"))
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


# 🚀 Main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("voice", voice_command))

    print("✅ Bot is running... Use /voice <text> to generate speech")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot stopped.")

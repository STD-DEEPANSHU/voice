import os
import asyncio
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation state
ASK_VOICE_TEXT = 1


# 🎙️ ElevenLabs Text-to-Speech
def text_to_speech(text):
    if not ELEVEN_API_KEY or not VOICE_ID:
        raise ValueError("ELEVEN_API_KEY or VOICE_ID not found in environment.")

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
            "speed": 0.95,
        },
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

    file_path = "voice.mp3"
    with open(file_path, "wb") as f:
        f.write(response.content)

    return file_path


# 🧠 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Type /voice to generate speech from text using ElevenLabs."
    )


# 🗣️ /voice command
async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗣️ Send me the text you want to convert into voice.")
    return ASK_VOICE_TEXT


# 🎧 Handle next message after /voice
async def handle_voice_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user.first_name
    logger.info(f"{user} requested voice for text: {text}")

    try:
        file_path = text_to_speech(text)
        await update.message.reply_audio(audio=open(file_path, "rb"))
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

    return ConversationHandler.END


# 🚫 Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Voice generation cancelled.")
    return ConversationHandler.END


# 🚀 Main function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation Handler (for /voice)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("voice", voice_command)],
        states={
            ASK_VOICE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_voice_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("✅ Bot is running... (use /voice to generate audio)")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot stopped.")

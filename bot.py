import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

print("BOT_TOKEN loaded:", "Yes" if BOT_TOKEN else "No")
print("ELEVEN_API_KEY loaded:", "Yes" if ELEVEN_API_KEY else "No")
print("VOICE_ID:", VOICE_ID)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 🎙️ Function to convert text to speech using ElevenLabs
def text_to_speech(text):
    if not ELEVEN_API_KEY or not VOICE_ID:
        raise ValueError("ELEVEN_API_KEY or VOICE_ID not found in environment.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    # 🧩 Added voice settings for slower, smoother voice
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,          # emotion consistency
            "similarity_boost": 0.85,  # clarity
            "style": 0.4,              # tone softness
            "use_speaker_boost": True,
            "speed": 0.85              # 👈 slower tempo (1.0 = normal)
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

    with open("voice.mp3", "wb") as f:
        f.write(response.content)

    return "voice.mp3"


# 🧠 Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Send me any text, and I’ll reply with a generated voice!")


# 🗣️ Handle text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user.first_name
    logger.info(f"Received message from {user}: {text}")

    try:
        file_path = text_to_speech(text)
        await update.message.reply_audio(audio=open(file_path, "rb"))
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


# 🚀 Main function
async def main():
    print("🚀 Starting Telegram bot...")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ✅ Clean and stable polling setup (no loop conflict)
    await app.initialize()
    await app.start()
    print("✅ Bot is now running!")
    await app.updater.start_polling()
    await asyncio.Event().wait()  # Keeps the bot running


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot stopped.")

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from elevenlabs.client import ElevenLabs

# ==================== CONFIG ====================
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "63c5214a34623f95fb43197a327aa1714a42bafc3a2c0f30bdc2aa880da8b08e")
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN", "8391689333:AAHpB8bhX8HTB70p60VoJkECe8tSdnp9HJI")
VOICE_ID = os.getenv("VOICE_ID", "P5wAx6EHfP4HolovAVoY")

# ElevenLabs client
client = ElevenLabs(api_key=ELEVEN_API_KEY)

# ==================== LOGGER ====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== COMMAND HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙 Send any text — I’ll reply with a voice message!")

async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user.first_name
    logger.info(f"🗣 {user} said: {text}")

    await update.message.reply_text("🎧 Generating voice, please wait...")

    try:
        audio = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            text=text,
            output_format="mp3_44100_128"
        )

        with open("voice.mp3", "wb") as f:
            f.write(audio)

        await update.message.reply_audio(audio=open("voice.mp3", "rb"))
        logger.info("✅ Voice message sent successfully")

    except Exception as e:
        logger.error(f"❌ Voice generation failed: {e}")
        await update.message.reply_text("⚠️ Voice generation failed. Please try again later.")

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("🤖 Voice bot is running...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, speak))

    app.run_polling()

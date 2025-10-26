import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from elevenlabs import generate, save, set_api_key

# ==================== CONFIG ====================
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
VOICE_ID = os.getenv("VOICE_ID", "P5wAx6EHfP4HolovAVoY")

set_api_key(ELEVEN_API_KEY)

# ==================== LOGGER ====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== COMMAND HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙 Send me any text — I’ll reply with a voice message!")

async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user.first_name
    logger.info(f"🗣 {user} said: {text}")

    await update.message.reply_text("🎧 Generating voice, please wait...")

    try:
        audio = generate(
            text=text,
            voice=VOICE_ID,
            model="eleven_multilingual_v2"
        )

        save(audio, "voice.mp3")
        await update.message.reply_audio(audio=open("voice.mp3", "rb"))
        logger.info("✅ Voice message sent successfully")

    except Exception as e:
        logger.error(f"❌ Voice generation failed: {e}")
        await update.message.reply_text("⚠️ Failed to generate voice. Please try again later.")

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("🤖 Voice bot is running...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, speak))

    app.run_polling()

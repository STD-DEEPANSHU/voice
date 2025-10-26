import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from elevenlabs import ElevenLabs

# ========== CONFIG ==========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Render me ENV var me add karna
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Render me ENV var me add karna
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # apna desired ElevenLabs voice id daal

# ========== LOGGING ==========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== ElevenLabs Client ==========
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# ========== /start Command ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙 Send me any text and I'll reply with a voice message!")

# ========== Text to Speech Function ==========
async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        await update.message.reply_text("🎧 Generating voice, please wait...")

        # ElevenLabs TTS convert
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        # Convert generator → bytes
        audio_bytes = b"".join(audio)

        # Save to file
        filename = "output.mp3"
        with open(filename, "wb") as f:
            f.write(audio_bytes)

        # Send voice file
        await update.message.reply_voice(voice=open(filename, "rb"))

    except Exception as e:
        logger.error(f"Error in text_to_speech: {e}")
        await update.message.reply_text("⚠️ Something went wrong while generating voice.")

# ========== MAIN APP ==========
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))

    logger.info("🤖 Bot started successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()

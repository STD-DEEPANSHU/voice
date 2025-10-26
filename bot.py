import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from elevenlabs.client import ElevenLabs  # ✅ correct import

# ========== CONFIG ==========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"

# ========== LOGGING ==========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== ElevenLabs Client ==========
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙 Send me text and I’ll reply with a voice message!")

# ========== Text-to-Speech ==========
async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        await update.message.reply_text("🎧 Generating voice...")

        # ElevenLabs streaming
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        # Write generator to file
        with open("voice.mp3", "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        await update.message.reply_voice(voice=open("voice.mp3", "rb"))

    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        await update.message.reply_text("⚠️ Voice generation failed. Check logs!")

# ========== MAIN ==========
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))

    logger.info("🤖 Bot started successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()

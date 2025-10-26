from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from elevenlabs import ElevenLabs
import os

# ==================== CONFIG ====================
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "63c5214a34623f95fb43197a327aa1714a42bafc3a2c0f30bdc2aa880da8b08e")
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN", "8391689333:AAHpB8bhX8HTB70p60VoJkECe8tSdnp9HJI")
VOICE_ID = os.getenv("VOICE_ID", "P5wAx6EHfP4HolovAVoY")  # Default if not set

client = ElevenLabs(api_key=ELEVEN_API_KEY)

# ==================== HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙 Send me any text and I’ll speak it using ElevenLabs voice!")

async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🎧 Generating voice...")

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    with open("voice.mp3", "wb") as f:
        f.write(audio)

    await update.message.reply_audio(audio=open("voice.mp3", "rb"))

# ==================== RUN BOT ====================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, speak))
app.run_polling()

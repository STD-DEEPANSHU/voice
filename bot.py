from elevenlabs.client import ElevenLabs
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import ELEVENLABS_API_KEY, TELEGRAM_BOT_TOKEN, VOICE_ID

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙️ Send me any text and I’ll reply with a voice message!")

async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    with open("voice.mp3", "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)

    await update.message.reply_voice(voice=open("voice.mp3", "rb"))

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))

if __name__ == "__main__":
    print("✅ Voice bot is running...")
    app.run_polling()

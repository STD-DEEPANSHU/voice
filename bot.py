import os
import asyncio
import logging
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables (works locally too)
load_dotenv()

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID", "A5W9pR9OjIbu80J0WuDW")  # default fallback

# Debug prints to Heroku logs
print("BOT_TOKEN loaded:", "Yes" if BOT_TOKEN else "❌ Missing")
print("ELEVEN_API_KEY loaded:", "Yes" if ELEVEN_API_KEY else "❌ Missing")
print("VOICE_ID:", VOICE_ID)

# Safety check
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found! Set it with: heroku config:set BOT_TOKEN=your_token")

if not ELEVEN_API_KEY:
    raise ValueError("❌ ELEVEN_API_KEY not found! Set it with: heroku config:set ELEVEN_API_KEY=your_key")

# Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙️ Welcome! Send me any text and I’ll reply with a voice message using ElevenLabs TTS.")

# Text handler (main TTS logic)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user.first_name

    await update.message.reply_text(f"🕐 Generating voice for: “{text}”...")

    # ElevenLabs API URL
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }

    # Call ElevenLabs API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    await update.message.reply_text(f"❌ ElevenLabs API Error: {response.status}")
                    return

                audio_data = await response.read()

                # Save temporary file
                file_path = f"{update.message.message_id}.mp3"
                with open(file_path, "wb") as f:
                    f.write(audio_data)

                # Send voice to user
                with open(file_path, "rb") as audio_file:
                    await update.message.reply_voice(voice=audio_file, caption=f"🎧 Here’s your voice, {user}!")

                os.remove(file_path)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Failed to generate voice. Please try again.")

# Main app
async def main():
    print("🚀 Starting Telegram bot...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

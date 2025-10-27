import os
import asyncio
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import httpx
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters


load_dotenv()


TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ELEVEN_API_KEY = os.environ.get('ELEVEN_API_KEY')
DEFAULT_VOICE = os.environ.get('VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
MODEL_ID = os.environ.get('MODEL_ID', 'eleven_multilingual_v2')


# In-memory per-chat voice mapping. For production, persist in DB.
chat_voice_map = {}


ELEVEN_BASE = 'https://api.elevenlabs.io/v1/text-to-speech'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
"Hello! Send me text and I'll reply with speech.\nUse /voice <voice_id> to set voice for this chat.\nExample: /voice 21m00Tcm4TlvDq8ikWAM"
)




async def set_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
chat_id = update.effective_chat.id
args = context.args
if not args:
await update.message.reply_text("Usage: /voice <voice_id> — current: {}".format(chat_voice_map.get(chat_id, DEFAULT_VOICE)))
return
voice_id = args[0].strip()
chat_voice_map[chat_id] = voice_id
await update.message.reply_text(f"Voice for this chat set to: {voice_id}")




async def tts_text(text: str, voice_id: str):
"""Call ElevenLabs API (async) and return bytes of audio (mp3) or raise."""
url = f"{ELEVEN_BASE}/{voice_id}"
headers = {
"Accept": "audio/mpeg",
"Content-Type": "application/json",
"xi-api-key": ELEVEN_API_KEY,
}
payload = {
"text": text,
"model_id": MODEL_ID,
"voice_settings": {"stability": 0.4, "similarity_boost": 0.75}
}


async with httpx.AsyncClient(timeout=30.0) as client:
resp = await client.post(url, headers=headers, json=payload)
if resp.status_code == 200:
return resp.content
else:
raise RuntimeError(f"ElevenLabs API error {resp.status_code}: {resp.text}")




async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
print("Stopped")

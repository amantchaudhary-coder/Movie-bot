import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID", "29731671"))
API_HASH = os.environ.get("API_HASH", "b2f676c8cb080b067cfd8b31a89ffc71")
BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4"

app = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

STREAM_BASE_URL = "https://movie-bot-liart.vercel.app/stream?id="

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 नमस्ते! मैं आपका Movie Streaming Bot हूँ।\n"
        "मुझे कोई भी वीडियो या मूवी फाइल भेजें, और मैं आपको उसका ऑनलाइन स्ट्रीमिंग लिंक दे दूंगा!"
    )

@app.on_message(filters.video | filters.document)
async def handle_media(client, message):
    media = message.video or message.document
    file_id = media.file_id
    file_name = media.file_name or "video.mp4"
    
    stream_link = f"{STREAM_BASE_URL}{file_id}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Watch / Stream Online", url=stream_link)]
    ])
    
    await message.reply_text(
        f"📂 **File Name:** `{file_name}`\n\n"
        f"🔗 **Stream Link:**\n`{stream_link}`",
        reply_markup=keyboard,
        quote=True
    )

if __name__ == "__main__":
    print("Bot is starting with asyncio...")
    app.start()
    asyncio.get_event_loop().run_forever()

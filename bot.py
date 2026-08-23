import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# आपकी असली डिटेल्स यहाँ सेट हैं
API_ID = int(os.environ.get("API_ID", "29731671"))  # अगर Render/GitHub पर एनवायरनमेंट वेरिएबल न हो तो बदल सकते हैं
API_HASH = os.environ.get("API_HASH", "b2f676c8cb080b067cfd8b31a89ffc71")
BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4"

app = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# आपका नया Vercel स्ट्रीमिंग सर्वर लिंक
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
    
    # Vercel का स्ट्रीमिंग लिंक बनाएं
    stream_link = f"{STREAM_BASE_URL}{file_id}"
    
    # यूजर को बटन के साथ लिंक भेजें
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
    print("Bot is starting...")
    app.run()

import os
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 611335
API_HASH = "1cbd415444b20757d77b06a4b12d1b77"
BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_lcqHm2kGed4"

app = Client(
    "movie_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Render के लिए डमी वेब सर्वर ताकि सर्विस बंद न हो
async def handle(request):
    return web.Response(text="Movie Bot is Running!")

async def web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text("नमस्ते! मुझे कोई भी वीडियो या फाइल भेजें, मैं आपको उसका डायरेक्ट लिंक देता हूँ।")

@app.on_message(filters.document | filters.video)
async def link_generator(client, message: Message):
    media = message.video or message.document
    file_name = media.file_name if hasattr(media, "file_name") else "video.mp4"
    
    file_path = await client.download_media(message)
    app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
    download_link = f"{app_url}/download/{file_name}"
    
    await message.reply_text(
        f"✅ **लिंक तैयार है!**\n\n📁 **फाइल नाम:** `{file_name}`\n🔗 **डायरेक्ट लिंक:**\n`{download_link}`",
        quote=True
    )

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(web_server())
    app.run()

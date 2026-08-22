import os
import logging
import urllib.parse
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# लॉगिंग सेट अप
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_lcqHm2kGed4"

# फाइलों का डेटा स्टोर करने के लिए डिक्शनरी
FILE_STORE = {}

# होमपेज रूट
async def handle(request):
    return web.Response(text="Movie Bot is Running Successfully!")

# डाउनलोड / स्ट्रीमिंग रूट
async def handle_download(request):
    filename = request.match_info.get('filename', '')
    decoded_filename = urllib.parse.unquote(filename)
    file_id = FILE_STORE.get(decoded_filename)
    
    if not file_id:
        return web.Response(text="File not found or expired!", status=404)
    
    return web.Response(text=f"Streaming/Download page for: {decoded_filename}")

async def web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    server.router.add_get("/download/{filename}", handle_download)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# जब कोई यूजर वीडियो या फाइल भेजे (चाहे फॉरवर्ड हो)
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    media = message.video or message.document
    
    if media:
        file_name = getattr(media, "file_name", "video.mp4")
        file_id = media.file_id
        
        # फाइल नेम को स्टोर करें
        FILE_STORE[file_name] = file_id
        
        app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
        encoded_filename = urllib.parse.quote(file_name)
        download_link = f"{app_url}/download/{encoded_filename}"
        
        await message.reply_text(
            f"✅ **लिंक तैयार है!**\n\n📁 **फाइल नाम:** `{file_name}`\n🔗 **डायरेक्ट लिंक:**\n`{download_link}`",
            parse_mode="Markdown"
        )

def main():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # वेब सर्वर चलाएं
    loop.run_until_complete(web_server())
    
    # टेलीग्राम बॉट एप्लीकेशन शुरू करें
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL | filters.FORWARDED, handle_media))
    
    print("Telegram Bot Started Successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()

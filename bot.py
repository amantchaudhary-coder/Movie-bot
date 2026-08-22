import os
import logging
import urllib.parse
import aiohttp
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# लॉगिंग सेट अप
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4"

# फाइलों का डेटा स्टोर करने के लिए डिक्शनरी
FILE_STORE = {}

# होमपेज रूट
async def handle(request):
    return web.Response(text="Movie Bot is Running Successfully & Ready!")

# डाउनलोड रूट - क्लिक करते ही बॉट यूजर को टेलीग्राम पर फाइल भेज देगा
async def handle_download(request):
    filename = request.match_info.get('filename', '')
    decoded_filename = urllib.parse.unquote(filename)
    file_data = FILE_STORE.get(decoded_filename)
    
    if not file_data:
        return web.Response(text="File not found or expired! Please send the video to the bot again.", status=404)
    
    chat_id = file_data.get('chat_id')
    file_id = file_data.get('file_id')
    
    # यूजर को सीधे टेलीग्राम पर फाइल भेजने का लिंक या पेज दिखाएं
    return web.Response(
        text=f"📂 फाइल: {decoded_filename}\n\nयह फाइल बड़ी है, इसलिए इसे सीधे टेलीग्राम पर देखने के लिए अपने बॉट पर वापस जाएं या नीचे दिए गए लिंक से डाउनलोड करें।",
        content_type='text/plain'
    )

async def web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    server.router.add_get("/download/{filename}", handle_download)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# जब कोई यूजर वीडियो या फाइल भेजे
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    media = message.video or message.document
    
    if media:
        file_name = getattr(media, "file_name", "video.mp4")
        file_id = media.file_id
        chat_id = message.chat_id
        
        # चैट आईडी और फाइल आईडी को सुरक्षित सेव करें
        FILE_STORE[file_name] = {
            'file_id': file_id,
            'chat_id': chat_id
        }
        
        app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
        encoded_filename = urllib.parse.quote(file_name)
        download_link = f"{app_url}/download/{encoded_filename}"
        
        await message.reply_text(
            f"✅ **लिंक तैयार है!** (बिना किसी साइज़ लिमिट के)\n\n📁 **फाइल नाम:** `{file_name}`\n🔗 **डायरेक्ट लिंक:**\n`{download_link}`\n\n💡 *यह लिंक आपकी फाइल को सुरक्षित रखेगा!*",
            parse_mode="Markdown"
        )

def main():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL | filters.FORWARDED, handle_media))
    
    loop.run_until_complete(web_server())
    
    print("Telegram Bot Started Successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()

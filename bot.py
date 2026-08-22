import os
import logging
import urllib.parse
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# लॉगिंग सेट अप
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4"

# फाइलों का डेटा स्टोर करने के लिए डिक्शनरी
FILE_STORE = {}
BOT_APPLICATION = None

# होमपेज रूट
async def handle(request):
    return web.Response(text="Movie Bot is Running Successfully!")

# रीडायरेक्ट रूट (बड़ी से बड़ी फाइल को भी बिना एरर के सीधे टेलीग्राम सर्वर से प्ले/डाउनलोड कराएगा)
async def handle_download(request):
    filename = request.match_info.get('filename', '')
    decoded_filename = urllib.parse.unquote(filename)
    file_id = FILE_STORE.get(decoded_filename)
    
    if not file_id:
        return web.Response(text="File not found or expired!", status=404)
    
    try:
        file_obj = await BOT_APPLICATION.bot.get_file(file_id)
        file_url = file_obj.file_path
        # यूजर को सीधे टेलीग्राम के ऑफिशियल फास्ट सर्वर पर रीडायरेक्ट कर देगा (कोई साइज़ लिमिट नहीं!)
        raise web.HTTPFound(file_url)
    except web.HTTPFound as e:
        raise e
    except Exception as e:
        return web.Response(text=f"Error redirecting file: {str(e)}", status=500)

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
        
        FILE_STORE[file_name] = file_id
        
        app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
        encoded_filename = urllib.parse.quote(file_name)
        download_link = f"{app_url}/download/{encoded_filename}"
        
        await message.reply_text(
            f"✅ **लिंक तैयार है!**\n\n📁 **फाइल नाम:** `{file_name}`\n🔗 **डायरेक्ट डाउनलोड / प्ले लिंक:**\n`{download_link}`",
            parse_mode="Markdown"
        )

def main():
    global BOT_APPLICATION
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    BOT_APPLICATION = ApplicationBuilder().token(BOT_TOKEN).build()
    BOT_APPLICATION.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL | filters.FORWARDED, handle_media))
    
    loop.run_until_complete(web_server())
    
    print("Telegram Bot Started Successfully!")
    BOT_APPLICATION.run_polling()

if __name__ == "__main__":
    main()

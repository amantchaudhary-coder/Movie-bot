import os
import logging
import urllib.parse
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# लॉगिंग सेट अप
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4"

# डाउनलोड्स को सेव करने के लिए लोकल फोल्डर
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# होमपेज रूट
async def handle(request):
    return web.Response(text="Custom Movie Server is Active!")

# डायरेक्ट डाउनलोड और स्ट्रीमिंग रूट (वेबसाइट और ऐप के लिए)
async def handle_download(request):
    filename = request.match_info.get('filename', '')
    decoded_filename = urllib.parse.unquote(filename)
    file_path = os.path.join(DOWNLOAD_DIR, decoded_filename)
    
    if os.path.exists(file_path):
        return webbrowser_file_response(request, file_path, decoded_filename)
    else:
        return web.Response(text="File not found on server!", status=404)

def webbrowser_file_response(request, file_path, filename):
    # aiohttp से फाइल को सीधे ब्राउज़र या वेबसाइट प्लेयर पर स्ट्रीम करें
    return web.FileResponse(file_path)

async def web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    server.router.add_get("/dl/{filename}", handle_download)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# जब यूजर बॉट पर वीडियो या फाइल भेजेगा
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    media = message.video or message.document
    
    if media:
        file_name = getattr(media, "file_name", "movie.mp4")
        # सुरक्षित फाइल नाम बनाएं
        file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        
        waiting_msg = await message.reply_text("⏳ फाइल सर्वर पर प्रोसेस हो रही है, कृपया प्रतीक्षा करें...")
        
        try:
            # टेलीग्राम से फाइल डाउनलोड करें
            file_obj = await context.bot.get_file(media.file_id)
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            await file_obj.download_to_drive(file_path)
            
            app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
            encoded_filename = urllib.parse.quote(file_name)
            direct_link = f"{app_url}/dl/{encoded_filename}"
            
            embed_code = f'<video controls width="100%"><source src="{direct_link}" type="video/mp4"></video>'
            
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=waiting_msg.message_id,
                text=f"✅ **लिंक सफलतापूर्वक तैयार हो गया है!**\n\n📁 **फाइल:** `{file_name}`\n🔗 **डायरेक्ट लिंक:**\n`{direct_link}`\n\n💻 **वेबसाइट/ऐप HTML Code:**\n`{embed_code}`",
                parse_mode="Markdown"
            )
        except Exception as e:
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=waiting_msg.message_id,
                text=f"❌ त्रुटि आ गई: {str(e)}"
            )

def main():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL | filters.FORWARDED, handle_media))
    
    loop.run_until_complete(web_server())
    
    print("Custom File Bot Started Successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()

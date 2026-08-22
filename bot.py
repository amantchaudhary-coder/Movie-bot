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

# वीडियो स्ट्रीमिंग रूट (क्लिक करते ही वीडियो प्ले/डाउनलोड होगा)
async def handle_download(request):
    filename = request.match_info.get('filename', '')
    decoded_filename = urllib.parse.unquote(filename)
    file_id = FILE_STORE.get(decoded_filename)
    
    if not file_id:
        return web.Response(text="File not found or expired!", status=404)
    
    try:
        # टेलीग्राम से फाइल की जानकारी प्राप्त करें
        file_obj = await BOT_APPLICATION.bot.get_file(file_id)
        file_url = file_obj.file_path
        
        # aiohttp की मदद से टेलीग्राम सर्वर से वीडियो स्ट्रीम को यूजर के ब्राउज़र पर भेजें
        import aiohttp
        async def stream_generator():
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    async for chunk in resp.content.iter_any():
                        yield chunk

        response = web.StreamResponse()
        response.content_type = 'video/mp4'
        response.headers['Content-Disposition'] = f'inline; filename="{decoded_filename}"'
        await response.prepare(request)
        
        async for chunk in stream_generator():
            await response.write(chunk)
            
        await response.write_eof()
        return response
        
    except Exception as e:
        return web.Response(text=f"Error streaming file: {str(e)}", status=500)

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
            f"✅ **लिंक तैयार है!**\n\n📁 **फाइल नाम:** `{file_name}`\n🔗 **ऑनलाइन प्ले / डायरेक्ट लिंक:**\n`{download_link}`",
            parse_mode="Markdown"
        )

def main():
    global BOT_APPLICATION
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # टेलीग्राम बॉट एप्लीकेशन बनाएं
    BOT_APPLICATION = ApplicationBuilder().token(BOT_TOKEN).build()
    BOT_APPLICATION.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL | filters.FORWARDED, handle_media))
    
    # वेब सर्वर शुरू करें
    loop.run_until_complete(web_server())
    
    print("Telegram Bot Started Successfully!")
    BOT_APPLICATION.run_polling()

if __name__ == "__main__":
    main()

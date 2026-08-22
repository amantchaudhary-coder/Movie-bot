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
BOT_APPLICATION = None

# होमपेज रूट
async def handle(request):
    return web.Response(text="Direct Movie Streaming Server is Live!")

# डायरेक्ट वीडियो स्ट्रीमिंग रूट (बिना डाउनलोड किए वेबसाइट पर लाइव चलेगा)
async def handle_stream(request):
    filename = request.match_info.get('filename', '')
    decoded_filename = urllib.parse.unquote(filename)
    file_id = FILE_STORE.get(decoded_filename)
    
    if not file_id:
        return web.Response(text="Movie not found or expired!", status=404)
    
    try:
        # टेलीग्राम सर्वर से फाइल का डायरेक्ट पाथ प्राप्त करें
        file_obj = await BOT_APPLICATION.bot.get_file(file_id)
        file_url = file_obj.file_path
        
        # aiohttp की मदद से टेलीग्राम से वीडियो चंक्स को सीधे यूजर के ब्राउज़र/वेबसाइट प्लेयर पर स्ट्रीम करें
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
        return web.Response(text=f"Streaming Error: {str(e)}", status=500)

async def web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    server.router.add_get("/stream/{filename}", handle_stream)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# जब कोई यूजर वीडियो या मूवी भेजे
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    media = message.video or message.document
    
    if media:
        file_name = getattr(media, "file_name", "movie.mp4")
        file_id = media.file_id
        
        FILE_STORE[file_name] = file_id
        
        app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
        encoded_filename = urllib.parse.quote(file_name)
        stream_link = f"{app_url}/stream/{encoded_filename}"
        
        # वेबसाइट के लिए HTML वीडियो एम्बेड कोड भी साथ में दे देंगे ताकि कॉपी करना आसान हो
        embed_code = f'<video controls width="100%"><source src="{stream_link}" type="video/mp4"></video>'
        
        await message.reply_text(
            f"✅ **लाइव स्ट्रीमिंग लिंक तैयार है!**\n\n📁 **मूवी:** `{file_name}`\n🔗 **डायरेक्ट स्ट्रीम लिंक:**\n`{stream_link}`\n\n💻 **वेबसाइट के लिए HTML Code:**\n`{embed_code}`",
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
    
    print("Direct Streaming Bot Started Successfully!")
    BOT_APPLICATION.run_polling()

if __name__ == "__main__":
    main()

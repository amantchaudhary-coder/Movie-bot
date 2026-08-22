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

# होमपेज रूट
async def handle(request):
    return web.Response(text="Movie Streaming Server is Live & Ready!")

# मूवी प्लेयर वेबपेज रूट - वेबसाइट और ऐप के लिए
async def handle_player(request):
    filename = request.match_info.get('filename', '')
    decoded_filename = urllib.parse.unquote(filename)
    file_id = FILE_STORE.get(decoded_filename)
    
    if not file_id:
        return web.Response(text="Movie not found or expired!", status=404)
    
    # खूबसूरत HTML5 वीडियो प्लेयर जो टेलीग्राम बॉट चैट पर रीडायरेक्ट करेगा या वीडियो दिखाएगा
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{decoded_filename} - Movie Player</title>
        <style>
            body {{
                background-color: #0f172a;
                color: #ffffff;
                font-family: Arial, sans-serif;
                margin: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                text-align: center;
                padding: 20px;
            }}
            .card {{
                background: #1e293b;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
                max-width: 500px;
                width: 100%;
            }}
            h2 {{
                font-size: 1.3rem;
                margin-bottom: 20px;
            }}
            a.btn {{
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                font-size: 1rem;
                margin-top: 10px;
            }}
            a.btn:hover {{
                background: #1d4ed8;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎬 {decoded_filename}</h2>
            <p style="color: #94a3b8; margin-bottom: 20px;">यह मूवी हाई-क्वालिटी में उपलब्ध है। इसे देखने के लिए नीचे दिए गए बटन पर क्लिक करें:</p>
            <a class="btn" href="https://t.me/movieadda10_bot" target="_blank">Telegram पर देखें / चलाएं</a>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

async def web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    server.router.add_get("/play/{filename}", handle_player)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# जब कोई यूजर वीडियो या फाइल भेजे (बिना साइज़ लिमिट के तुरंत लिंक देगा)
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    media = message.video or message.document
    
    if media:
        file_name = getattr(media, "file_name", "movie.mp4")
        file_id = media.file_id
        
        # फाइल आईडी को सेव करें (अब get_file का झंझट ही खत्म!)
        FILE_STORE[file_name] = file_id
        
        app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
        encoded_filename = urllib.parse.quote(file_name)
        watch_link = f"{app_url}/play/{encoded_filename}"
        
        await message.reply_text(
            f"✅ **वेबसाइट/ऐप के लिए लिंक तैयार है!** (कोई साइज़ लिमिट नहीं)\n\n📁 **मूवी नाम:** `{file_name}`\n🔗 **वेब लिंक (इसे अपने पोस्टर/बटन में लगाएं):**\n`{watch_link}`",
            parse_mode="Markdown"
        )

def main():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL | filters.FORWARDED, handle_media))
    
    loop.run_until_complete(web_server())
    
    print("Movie Bot Started Successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()

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

# मूवी प्लेयर वेबपेज रूट - यही पेज आपकी वेबसाइट/ऐप पर खुलेगा
async def handle_player(request):
    filename = request.match_info.get('filename', '')
    decoded_filename = urllib.parse.unquote(filename)
    file_data = FILE_STORE.get(decoded_filename)
    
    if not file_data:
        return web.Response(text="Movie not found or expired!", status=404)
    
    file_url = file_data.get('file_url', '')
    
    # खूबसूरत HTML5 वीडियो प्लेयर पेज जो मोबाइल ऐप और वेबसाइट दोनों पर मक्खन की तरह चलेगा
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
            }}
            .video-container {{
                width: 100%;
                max-width: 900px;
                background: #000;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            }}
            video {{
                width: 100%;
                height: auto;
                display: block;
            }}
            h2 {{
                margin-top: 15px;
                font-size: 1.2rem;
                text-align: center;
                padding: 0 10px;
            }}
        </style>
    </head>
    <body>
        <div class="video-container">
            <video controls autoplay playsinline>
                <source src="{file_url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <h2>🎬 {decoded_filename}</h2>
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

# जब कोई यूजर वीडियो या फाइल भेजे
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    media = message.video or message.document
    
    if media:
        file_name = getattr(media, "file_name", "movie.mp4")
        file_id = media.file_id
        
        try:
            # टेलीग्राम से डायरेक्ट डाउनलोड लिंक प्राप्त करें
            file_obj = await context.bot.get_file(file_id)
            file_url = file_obj.file_path
            
            # डेटा स्टोर करें
            FILE_STORE[file_name] = {
                'file_url': file_url
            }
            
            app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
            encoded_filename = urllib.parse.quote(file_name)
            watch_link = f"{app_url}/play/{encoded_filename}"
            
            await message.reply_text(
                f"✅ **वेबसाइट/ऐप के लिए प्लेयर लिंक तैयार है!**\n\n📁 **मूवी नाम:** `{file_name}`\n🔗 **वॉच लिंक (इसे अपने पोस्टर/बटन में लगाएं):**\n`{watch_link}`",
                parse_mode="Markdown"
            )
        except Exception as e:
            await message.reply_text(f"⚠️ त्रुटि: {str(e)}\n\n(यदि फाइल बहुत बड़ी है, तो छोटी क्लिप या कॉम्प्रेस वीडियो से टेस्ट करें!)")

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

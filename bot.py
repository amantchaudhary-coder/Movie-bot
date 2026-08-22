import os
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# लॉगिंग सेट अप
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_lcqHm2kGed4"

# Render के लिए डमी वेब सर्वर ताकि सर्विस हमेशा चालू रहे
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

# जब कोई यूजर वीडियो या फाइल भेजे
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    media = message.video or message.document
    
    if media:
        file_name = getattr(media, "file_name", "video.mp4")
        app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://movie-bot-7457.onrender.com")
        download_link = f"{app_url}/download/{file_name}"
        
        await message.reply_text(
            f"✅ **लिंक तैयार है!**\n\n📁 **फाइल नाम:** `{file_name}`\n🔗 **डायरेक्ट लिंक:**\n`{download_link}`",
            parse_mode="Markdown"
        )

def main():
    # वेब सर्वर और टेलीग्राम बॉट दोनों को एक साथ शुरू करने के लिए
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # वेब सर्वर चलाएं
    loop.run_until_complete(web_server())
    
    # टेलीग्राम बॉट एप्लीकेशन शुरू करें
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, handle_media))
    
    print("Telegram Bot Started Successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()

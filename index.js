const { Telegraf } = require('telegraf');

// आपका असली बॉट टोकन
const bot = new Telegraf('8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4');

const STREAM_BASE_URL = "https://movie-bot-liart.vercel.app/stream?id=";

bot.start((ctx) => {
    ctx.reply(
        "👋 नमस्ते! मैं आपका Movie Streaming Bot हूँ।\nमुझे कोई भी वीडियो या मूवी फाइल भेजें, और मैं आपको उसका ऑनलाइन स्ट्रीमिंग लिंक दे दूंगा!"
    );
});

bot.on(['video', 'document'], (ctx) => {
    const media = ctx.message.video || ctx.message.document;
    const fileId = media.file_id;
    const fileName = media.file_name || "video.mp4";
    
    const streamLink = `${STREAM_BASE_URL}${fileId}`;
    
    ctx.reply(
        `📂 **File Name:** \`${fileName}\`\n\n🔗 **Stream Link:**\n\`${streamLink}\``,
        {
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [
                    [{ text: "🚀 Watch / Stream Online", url: streamLink }]
                ]
            }
        }
    );
});

// पुरानी फंसी हुई रिक्वेस्ट्स को साफ़ करके बॉट लॉन्च करेगा
bot.launch({
    dropPendingUpdates: true
});

console.log("Node.js Telegram Bot is running successfully...");

const { Telegraf } = require('telegraf');

// आपका असली बॉट टोकन
const bot = new Telegraf('8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4');

// Vercel का स्ट्रीमिंग बेस यूआरएल (वीडियो स्ट्रीम करने के लिए)
const STREAM_BASE_URL = "https://movie-bot-liart.vercel.app/api/stream?id=";

// Render का यूआरएल (जहाँ आपका बॉट होस्ट है)
const RENDER_URL = "https://movie-bot-7457.onrender.com";

bot.start((ctx) => {
    ctx.reply(
        "👋 नमस्ते! मैं आपका Movie Streaming Bot हूँ।\nमुझे कोई भी वीडियो या मूवी फाइल भेजें, और मैं आपको उसका ऑनलाइन स्ट्रीमिंग लिंक दे दूंगा!"
    );
});

bot.on(['video', 'document'], (ctx) => {
    const media = ctx.message.video || ctx.message.document;
    if (!media) return;
    
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

// Render के लिए Webhook सेटअप
const PORT = process.env.PORT || 3000;
const WEBHOOK_PATH = `/telegraf/${bot.secretPathComponent()}`;

bot.telegram.setWebhook(`${RENDER_URL}${WEBHOOK_PATH}`);

const { createServer } = require('http');

createServer(bot.webhookCallback(WEBHOOK_PATH)).listen(PORT, () => {
    console.log(`Telegram bot webhook is running on port ${PORT}`);
});

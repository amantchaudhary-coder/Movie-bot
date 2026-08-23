const { Telegraf } = require('telegraf');

// आपका असली बॉट टोकन
const bot = new Telegraf('8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4');

const STREAM_BASE_URL = "https://movie-bot-liart.vercel.app/stream?id=";
// आपका Vercel का बेस डोमेन (जहाँ आपकी वेबसाइट/एप होस्ट है)
const VERCEL_URL = "https://movie-bot-liart.vercel.app";

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

// Render के लिए Webhook सेटअप (यह 409 एरर को हमेशा के लिए खत्म कर देगा)
const PORT = process.env.PORT || 3000;
const WEBHOOK_PATH = `/telegraf/${bot.secretPathComponent()}`;

bot.telegram.setWebhook(`${VERCEL_URL}${WEBHOOK_PATH}`);

// Express सर्वर या Telegraf का इन-बिल्ट वेबहुक हैंडलर शुरू करना
// चूंकि Render को एक वेब सर्विस चाहिए, हम webhookCallback का उपयोग कर रहे हैं:
const { createServer } = require('http');

createServer(bot.webhookCallback(WEBHOOK_PATH)).listen(PORT, () => {
    console.log(`Telegram bot webhook is running on port ${PORT}`);
});

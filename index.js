const { Telegraf } = require('telegraf');
const axios = require('axios');
const { createServer } = require('http');

// आपका असली बॉट टोकन
const BOT_TOKEN = '8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4';
const bot = new Telegraf(BOT_TOKEN);

// Render का आपका बेस यूआरएल (जहाँ बॉट और स्ट्रीमिंग दोनों चलेंगे)
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
    
    // अब स्ट्रीमिंग लिंक सीधे आपके Render सर्वर का होगा
    const streamLink = `${RENDER_URL}/stream?id=${fileId}`;
    
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

// HTTP सर्वर बनाएँ जो Telegram Webhook और Video Streaming दोनों को संभालेगा
const PORT = process.env.PORT || 3000;
const WEBHOOK_PATH = `/telegraf/${bot.secretPathComponent()}`;

bot.telegram.setWebhook(`${RENDER_URL}${WEBHOOK_PATH}`);

const server = createServer(async (req, res) => {
    const urlParts = new URL(req.url, `http://${req.headers.host}`);
    
    // अगर कोई स्ट्रीमिंग लिंक पर क्लिक करेगा, तो यह कोड वीडियो चलाएगा
    if (urlParts.pathname === '/stream') {
        const fileId = urlParts.searchParams.get('id');
        if (!fileId) {
            res.writeHead(400, { 'Content-Type': 'text/plain' });
            return res.end("Video ID is missing!");
        }

        try {
            const fileInfoUrl = `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`;
            const response = await axios.get(fileInfoUrl);

            if (!response.data.ok) {
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                return res.end("Video not found on Telegram.");
            }

            const filePath = response.data.result.file_path;
            const directVideoUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;

            // यूजर को सीधे टेलीग्राम के वीडियो पर रीडायरेक्ट कर देगा (वीडियो चलने लगेगा)
            res.writeHead(302, { Location: directVideoUrl });
            res.end();
        } catch (error) {
            console.error("Streaming Error:", error.message);
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end("Internal Server Error");
        }
        return;
    }

    // बाकी सभी रिक्वेस्ट Telegram Webhook के लिए Telegraf को पास कर दी जाएंगी
    bot.webhookCallback(WEBHOOK_PATH)(req, res);
});

server.listen(PORT, () => {
    console.log(`Bot and Stream server is running on port ${PORT}`);
});

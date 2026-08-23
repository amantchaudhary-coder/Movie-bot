const { Telegraf } = require('telegraf');
const { createServer } = require('http');

const BOT_TOKEN = '8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4';
const bot = new Telegraf(BOT_TOKEN);
const RENDER_URL = "https://movie-bot-7457.onrender.com";

bot.start((ctx) => {
    ctx.reply("👋 नमस्ते! आपका बॉट तैयार है। कोई भी वीडियो भेजें!");
});

bot.on(['video', 'document'], (ctx) => {
    const media = ctx.message.video || ctx.message.document;
    if (!media) return;
    
    const fileId = media.file_id;
    const fileName = media.file_name || "video.mp4";
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

const PORT = process.env.PORT || 3000;
const WEBHOOK_PATH = `/telegraf/${bot.secretPathComponent()}`;
bot.telegram.setWebhook(`${RENDER_URL}${WEBHOOK_PATH}`);

const server = createServer(async (req, res) => {
    const urlParts = new URL(req.url, `http://${req.headers.host}`);
    
    if (urlParts.pathname === '/stream') {
        const fileId = urlParts.searchParams.get('id');
        if (!fileId) {
            res.writeHead(400, { 'Content-Type': 'text/plain' });
            return res.end("Video ID is missing!");
        }

        try {
            const fileInfoUrl = `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`;
            const apiRes = await fetch(fileInfoUrl);
            const data = await apiRes.json();

            if (!data.ok) {
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                return res.end("Video not found on Telegram.");
            }

            const filePath = data.result.file_path;
            const directVideoUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;

            res.writeHead(302, { Location: directVideoUrl });
            res.end();
        } catch (error) {
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end("Internal Server Error: " + error.message);
        }
        return;
    }

    bot.webhookCallback(WEBHOOK_PATH)(req, res);
});

server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

const { Telegraf } = require('telegraf');
const express = require('express');
const axios = require('axios');

const BOT_TOKEN = '8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4';
const bot = new Telegraf(BOT_TOKEN);
const RENDER_URL = "https://movie-bot-7457.onrender.com";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req, res) => {
    res.send('Bot and Stream Server is Running Live!');
});

// वीडियो स्ट्रीमिंग रूट (अब यह ब्राउज़र में प्लेयर दिखाएगा)
app.get('/stream', async (req, res) => {
    const fileId = req.query.id;
    if (!fileId) {
        return res.status(400).send("Video ID is missing!");
    }

    try {
        const fileInfoUrl = `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`;
        const response = await axios.get(fileInfoUrl);

        if (!response.data.ok) {
            return res.status(404).send("Video not found on Telegram.");
        }

        const filePath = response.data.result.file_path;
        const directVideoUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;

        // ब्राउज़र के लिए एक खूबसूरत HTML5 वीडियो प्लेयर पेज रिटर्न करेगा
        res.send(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Movie Stream Player</title>
                <style>
                    body {
                        margin: 0;
                        background-color: #0f172a;
                        color: #fff;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        font-family: sans-serif;
                    }
                    video {
                        width: 100%;
                        max-width: 900px;
                        max-height: 80vh;
                        border-radius: 12px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    }
                    h2 {
                        margin-bottom: 15px;
                        font-size: 1.2rem;
                        color: #38bdf8;
                    }
                </style>
            </head>
            <body>
                <h2>🚀 Online Movie Stream Player</h2>
                <video controls autoplay>
                    <source src="${directVideoUrl}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </body>
            </html>
        `);
    } catch (error) {
        console.error("Streaming Error:", error.message);
        return res.status(500).send("Internal Server Error: " + error.message);
    }
});

// Telegram Webhook सेटअप
const WEBHOOK_PATH = `/telegraf/${bot.secretPathComponent()}`;
app.use(bot.webhookCallback(WEBHOOK_PATH));
bot.telegram.setWebhook(`${RENDER_URL}${WEBHOOK_PATH}`);

bot.start((ctx) => {
    ctx.reply("👋 नमस्ते! आपका बॉट पूरी तरह तैयार है। कोई भी वीडियो भेजें!");
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

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

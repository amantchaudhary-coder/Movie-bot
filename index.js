const { Telegraf } = require('telegraf');
const express = require('express');
const axios = require('axios');

const BOT_TOKEN = '8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4';
const bot = new Telegraf(BOT_TOKEN);
const RENDER_URL = "http://15.235.145.222:3000";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req, res) => {
    res.send('Bot and Stream Server for Large Files is Running Live!');
});

// बड़ी फाइलों के लिए एडवांस्ड स्ट्रीमिंग रूट (Range Support के साथ)
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

        // अगर यूजर ने सीधे लिंक पर क्लिक किया है, तो हम सुंदर वीडियो प्लेयर पेज दिखाएंगे
        if (!req.headers.range) {
            return res.send(`
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>HD Movie Stream Player</title>
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
                            max-width: 950px;
                            max-height: 85vh;
                            border-radius: 12px;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
                        }
                        h2 {
                            margin-bottom: 15px;
                            font-size: 1.3rem;
                            color: #38bdf8;
                        }
                    </style>
                </head>
                <body>
                    <h2>🎬 HD Online Stream Player</h2>
                    <video controls autoplay>
                        <source src="/stream?id=${fileId}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </body>
                </html>
            `);
        }

        // बड़ी फाइल के लिए रेंज रिक्वेस्ट हैंडल करना (Fast Chunk Streaming)
        const headResponse = await axios.head(directVideoUrl);
        const fileSize = parseInt(headResponse.headers['content-length'], 10);
        const range = req.headers.range;

        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
        const chunksize = (end - start) + 1;

        const videoStream = await axios({
            method: 'get',
            url: directVideoUrl,
            headers: { Range: `bytes=${start}-${end}` },
            responseType: 'stream'
        });

        res.writeHead(206, {
            'Content-Range': `bytes ${start}-${end}/${fileSize}`,
            'Accept-Ranges': 'bytes',
            'Content-Length': chunksize,
            'Content-Type': 'video/mp4',
        });

        videoStream.data.pipe(res);

    } catch (error) {
        console.error("Streaming Error:", error.message);
        if (!res.headersSent) {
            return res.status(500).send("Internal Server Error: " + error.message);
        }
    }
});

// Telegram Webhook सेटअप
const WEBHOOK_PATH = `/telegraf/${bot.secretPathComponent()}`;
app.use(bot.webhookCallback(WEBHOOK_PATH));
bot.telegram.setWebhook(`${RENDER_URL}${WEBHOOK_PATH}`);

bot.start((ctx) => {
    ctx.reply("👋 नमस्ते! आपका HD Movie Streaming बॉट तैयार है। कोई भी बड़ी मूवी या वीडियो भेजें!");
});

bot.on(['video', 'document'], (ctx) => {
    const media = ctx.message.video || ctx.message.document;
    if (!media) return;
    
    const fileId = media.file_id;
    const fileName = media.file_name || "movie.mp4";
    const streamLink = `${RENDER_URL}/stream?id=${fileId}`;
    
    ctx.reply(
        `📂 **File Name:** \`${fileName}\`\n\n🔗 **Stream Link:**\n\`${streamLink}\``,
        {
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [
                    [{ text: "🚀 Watch HD Online", url: streamLink }]
                ]
            }
        }
    );
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

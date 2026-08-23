const axios = require('axios');

export default async function handler(req, res) {
    const { id } = req.query; // यह टेलीग्राम की file_id है जो लिंक से आएगी

    if (!id) {
        return res.status(400).send("Video ID is missing!");
    }

    const BOT_TOKEN = '8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4';

    try {
        // 1. टेलीग्राम से फाइल का पाथ (File Path) प्राप्त करें
        const fileInfoUrl = `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${id}`;
        const response = await axios.get(fileInfoUrl);

        if (!response.data.ok) {
            return res.status(404).send("Video not found on Telegram.");
        }

        const filePath = response.data.result.file_path;
        
        // 2. टेलीग्राम का असली डायरेक्ट वीडियो डाउनलोड/स्ट्रीम लिंक बनाएं
        const directVideoUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;

        // 3. यूजर को या वेबसाइट के वीडियो प्लेयर को इस डायरेक्ट लिंक पर रीडायरेक्ट कर दें
        res.writeHead(302, { Location: directVideoUrl });
        res.end();

    } catch (error) {
        console.error("Error fetching video from Telegram:", error);
        res.status(500).send("Internal Server Error");
    }
}

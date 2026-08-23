const axios = require('axios');

module.exports = async (req, res) => {
    const { id } = req.query;

    if (!id) {
        return res.status(400).send("Video ID is missing!");
    }

    const BOT_TOKEN = '8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4';

    try {
        const fileInfoUrl = `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${id}`;
        const response = await axios.get(fileInfoUrl);

        if (!response.data.ok) {
            return res.status(404).send("Video not found on Telegram.");
        }

        const filePath = response.data.result.file_path;
        const directVideoUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;

        // यूजर को सीधे टेलीग्राम के वीडियो लिंक पर रीडायरेक्ट कर देगा
        res.writeHead(302, { Location: directVideoUrl });
        res.end();

    } catch (error) {
        console.error("Error fetching video:", error.message);
        res.status(500).send("Internal Server Error");
    }
};

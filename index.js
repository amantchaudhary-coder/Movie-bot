const express = require('express');
const fetch = require('node-fetch');
const app = express();

const BOT_TOKEN = "8937136224:AAET5jgO2qAK5TDuUHq6hBj_1cqHm2kGed4";

app.get('/stream', async (req, res) => {
  const fileId = req.query.id;
  if (!fileId) {
    return res.status(400).send("Missing video ID");
  }

  try {
    const telegramApiUrl = `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`;
    const apiRes = await fetch(telegramApiUrl);
    const apiData = await apiRes.json();

    if (!apiData.ok || !apiData.result.file_path) {
      return res.status(500).send("Telegram API Error: " + (apiData.description || "Invalid file"));
    }

    const filePath = apiData.result.file_path;
    const downloadUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;

    const rangeHeader = req.headers.range;
    const fetchHeaders = {};
    if (rangeHeader) {
      fetchHeaders['Range'] = rangeHeader;
    }

    const videoRes = await fetch(downloadUrl, {
      method: req.method,
      headers: fetchHeaders
    });

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.status(videoRes.status);
    videoRes.headers.forEach((val, key) => {
      res.setHeader(key, val);
    });

    videoRes.body.pipe(res);
  } catch (err) {
    res.status(500).send("Error: " + err.message);
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

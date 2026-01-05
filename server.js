const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// CodeWords Service URLs
const SERVICES = {
  manga: 'https://codewords.agemo.ai/run/manga_scraper_catbox_400bda55',
  storage: 'https://codewords.agemo.ai/run/mongodb_storage_stats_a3ac1201',
  sync: 'https://codewords.agemo.ai/run/mongodb_master_sync_ff22188f'
};

// Import manga
app.post('/api/manga/import', async (req, res) => {
  try {
    const { source, manga_url, max_chapters } = req.body;
    
    console.log('Importing:', manga_url);
    
    const response = await axios.post(SERVICES.manga, {
      mode: 'url',
      source: source,
      manga_url: manga_url,
      max_chapters: max_chapters || 5
    }, {
      timeout: 180000
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('Import error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// Storage stats
app.post('/api/storage/stats', async (req, res) => {
  try {
    const response = await axios.post(SERVICES.storage, {});
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// DB sync
app.post('/api/db/sync', async (req, res) => {
  try {
    const response = await axios.post(SERVICES.sync, {});
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

// Root
app.get('/', (req, res) => {
  res.json({
    name: 'Comicktown API',
    endpoints: [
      'POST /api/manga/import',
      'POST /api/storage/stats',
      'POST /api/db/sync',
      'GET /health'
    ]
  });
});

app.listen(PORT, () => {
  console.log(`Server on port ${PORT}`);
});

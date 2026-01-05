const express = require('express');
const cors = require('cors');
const axios = require('axios');
const { MongoClient } = require('mongodb');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://wuwamuqo_db_user:NfhgBOs7LeRbSI6S@cluster0.zxqopbx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';

app.use(cors());
app.use(express.json());

const SERVICES = {
  manga: 'https://codewords.agemo.ai/run/manga_scraper_catbox_400bda55',
  batch: 'https://codewords.agemo.ai/run/manga_batch_uploader_95bae5eb',
  storage: 'https://codewords.agemo.ai/run/mongodb_storage_stats_a3ac1201',
  sync: 'https://codewords.agemo.ai/run/mongodb_master_sync_ff22188f'
};

// Import single manga
app.post('/api/manga/import', async (req, res) => {
  try {
    const { source, manga_url, max_chapters } = req.body;
    console.log('Importing:', manga_url);
    const response = await axios.post(SERVICES.manga, {
      mode: 'url', source, manga_url, max_chapters: max_chapters || 5
    }, { timeout: 180000 });
    res.json(response.data);
  } catch (error) {
    console.error('Import error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// Batch import manga
app.post('/api/manga/batch', async (req, res) => {
  try {
    console.log('Batch import:', req.body.manga_list?.length, 'manga');
    const response = await axios.post(SERVICES.batch, req.body, { timeout: 3600000 });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all manga from MongoDB
app.get('/api/manga/list', async (req, res) => {
  let client;
  try {
    client = new MongoClient(MONGODB_URI);
    await client.connect();
    const db = client.db('comicktown');
    const manga = await db.collection('manga_imports')
      .find({})
      .sort({ imported_at: -1 })
      .limit(100)
      .toArray();
        
    res.json({
      total: manga.length,
      manga: manga.map(m => ({
        id: m._id,
        title: m.title,
        source: m.source,
        url: m.url || m.source_url,
        chapters: m.chapters || [],
        total_chapters: m.total_chapters || m.chapters?.length || 0,
        status: m.status,
        imported_at: m.imported_at
      }))
    });
  } catch (error) {
    console.error('List error:', error.message);
    res.status(500).json({ error: error.message });
  } finally {
    if (client) await client.close();
  }
});

// Get single manga details
app.get('/api/manga/:id', async (req, res) => {
  let client;
  try {
    client = new MongoClient(MONGODB_URI);
    await client.connect();
    const db = client.db('comicktown');
    const manga = await db.collection('manga_imports').findOne({ _id: req.params.id });
    
    if (!manga) {
      return res.status(404).json({ error: 'Manga not found' });
    }
    
    res.json(manga);
  } catch (error) {
    res.status(500).json({ error: error.message });
  } finally {
    if (client) await client.close();
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
    version: '1.0.0',
    endpoints: [
      'POST /api/manga/import',
      'POST /api/manga/batch',
      'GET /api/manga/list',
      'GET /api/manga/:id',
      'POST /api/storage/stats',
      'POST /api/db/sync',
      'GET /health'
    ]
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Comicktown Backend on port ${PORT}`);
});

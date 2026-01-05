const express = require('express');
const cors = require('cors');
const axios = require('axios');
const { MongoClient } = require('mongodb');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://wuwamuqo_db_user:NfhgBOs7LeRbSI6S@cluster0.zxqopbx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';

const SUPABASE_URL = 'https://llirkgzjtaqltkxsgazo.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsaXJrZ3pqdGFxbHRreHNnYXpvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNDA4ODEsImV4cCI6MjA4MjcxNjg4MX0.z1e8g4GgGy1jQaykQ5AFHR2_kSD11GnsUYyV8t0g3TI';

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

// Batch import
app.post('/api/manga/batch', async (req, res) => {
  try {
    const response = await axios.post(SERVICES.batch, req.body, { timeout: 3600000 });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Sync MongoDB to Supabase (MAKES MANGA APPEAR ON SITE!)
app.post('/api/sync-to-site', async (req, res) => {
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    const db = client.db('comicktown');
    const mangaList = await db.collection('manga_imports').find({}).toArray();
    
    let synced = 0;
    let chapters_synced = 0;
    const errors = [];
    
    for (const manga of mangaList) {
      try {
        const { data: insertedManga, error } = await supabase
          .from('manga')
          .insert({
            title: manga.title,
            summary: Imported from ${manga.source},
            status: 'ongoing',
            author: manga.source,
            genres: [manga.source],
            rating: 0.0,
            view_count: 0
          })
          .select()
          .single();
        
        if (error) {
          errors.push(${manga.title}: ${error.message});
          continue;
        }
        
        synced++;
        
        const chapters = manga.chapters || [];
        for (const ch of chapters) {
          await supabase.from('chapters').insert({
            manga_id: insertedManga.id,
            chapter_number: String(ch.num),
            chapter_title: Chapter ${ch.num},
            pdf_url: ch.url,
            page_count: ch.images || 0
          });
          chapters_synced++;
        }
        
        console.log(Synced: ${manga.title} (${chapters.length} ch));
        
      } catch (err) {
        errors.push(${manga.title}: ${err.message});
      }
    }
    
    await client.close();
    
    res.json({
      status: 'success',
      synced_manga: synced,
      synced_chapters: chapters_synced,
      total: mangaList.length,
      errors: errors
    });
    
  } catch (error) {
    console.error('Sync error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// Get manga list
app.get('/api/manga/list', async (req, res) => {
  let client;
  try {
    client = new MongoClient(MONGODB_URI);
    await client.connect();
    const db = client.db('comicktown');
    const manga = await db.collection('manga_imports').find({}).sort({ imported_at: -1 }).limit(100).toArray();
    res.json({ total: manga.length, manga: manga });
  } catch (error) {
    res.status(500).json({ error: error.message });
  } finally {
    if (client) await client.close();
  }
});

// Get single manga
app.get('/api/manga/:id', async (req, res) => {
  let client;
  try {
    client = new MongoClient(MONGODB_URI);
    await client.connect();
    const db = client.db('comicktown');
    const manga = await db.collection('manga_imports').findOne({ _id: req.params.id });
    if (!manga) return res.status(404).json({ error: 'Not found' });
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

// Health
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
      'POST /api/sync-to-site',
      'GET /api/manga/list',
      'GET /api/manga/:id',
      'POST /api/storage/stats',
      'GET /health'
    ]
  });
});

app.listen(PORT, () => {
  console.log(🚀 Comicktown Backend on port ${PORT});
});

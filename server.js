import express from "express";
import cors from "cors";
import axios from "axios";
import { MongoClient } from "mongodb";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// All 3 MongoDB URIs
const MONGODB_URIS = [
  process.env.MONGODB_URI_1 || "mongodb+srv://probito140:umaid2008@cluster0.1utfc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
  process.env.MONGODB_URI_2 || "mongodb+srv://wuwamuqo_db_user:NfhgBOs7LeRbSI6S@cluster0.zxqopbx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
  process.env.MONGODB_URI_3 || "mongodb+srv://spxsolo:umaid2008@cluster0.7fbux.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
];

const PRIMARY_MONGODB_URI = MONGODB_URIS[0];

const SUPABASE_URL = process.env.SUPABASE_URL || "https://llirkgzjtaqltkxsgazo.supabase.co";
const SUPABASE_KEY = process.env.SUPABASE_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsaXJrZ3pqdGFxbHRreHNnYXpvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNDA4ODEsImV4cCI6MjA4MjcxNjg4MX0.z1e8g4GgGy1jQaykQ5AFHR2_kSD11GnsUYyV8t0g3TI";

const CODEWORDS_API_KEY = process.env.CODEWORDS_API_KEY || "";
const MANGA_SCRAPER_SERVICE = "manga_chapter_monitor_a00f7c06";

app.use(cors());
app.use(express.json());

// ==========================================
// MANGA ENDPOINTS
// ==========================================

// Get all manga
app.get("/api/manga", async (req, res) => {
  try {
    const { site, limit = 100 } = req.query;
    const client = new MongoClient(PRIMARY_MONGODB_URI);
    await client.connect();
    
    const db = client.db("comicktown");
    const query = site ? { site } : {};
    const manga = await db.collection("manga")
      .find(query)
      .limit(parseInt(limit))
      .toArray();
    
    await client.close();
    res.json({ manga, count: manga.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get chapters for a manga
app.get("/api/manga/:mangaUrl/chapters", async (req, res) => {
  try {
    const { mangaUrl } = req.params;
    const decodedUrl = decodeURIComponent(mangaUrl);
    
    const client = new MongoClient(PRIMARY_MONGODB_URI);
    await client.connect();
    
    const db = client.db("comicktown");
    const chapters = await db.collection("chapters")
      .find({ manga_url: decodedUrl })
      .sort({ number: -1 })
      .toArray();
    
    await client.close();
    res.json({ chapters, count: chapters.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Search manga
app.get("/api/search", async (req, res) => {
  try {
    const { q, site } = req.query;
    
    if (!q) {
      return res.status(400).json({ error: "Query parameter 'q' required" });
    }
    
    const client = new MongoClient(PRIMARY_MONGODB_URI);
    await client.connect();
    
    const db = client.db("comicktown");
    const query = {
      title: { $regex: q, $options: 'i' }
    };
    
    if (site) {
      query.site = site;
    }
    
    const manga = await db.collection("manga")
      .find(query)
      .limit(50)
      .toArray();
    
    await client.close();
    res.json({ manga, count: manga.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get latest updates
app.get("/api/latest", async (req, res) => {
  try {
    const { limit = 20 } = req.query;
    const client = new MongoClient(PRIMARY_MONGODB_URI);
    await client.connect();
    
    const db = client.db("comicktown");
    const chapters = await db.collection("chapters")
      .find({})
      .sort({ created_at: -1 })
      .limit(parseInt(limit))
      .toArray();
    
    await client.close();
    res.json({ chapters, count: chapters.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ==========================================
// SCRAPING TRIGGER
// ==========================================

app.post("/api/trigger-scrape", async (req, res) => {
  try {
    const response = await axios.post(
      `https://codewords.agemo.ai/run/${MANGA_SCRAPER_SERVICE}`,
      { force_check: true },
      {
        headers: {
          'Authorization': `Bearer ${CODEWORDS_API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 300000
      }
    );
    
    res.json({ 
      status: 'success', 
      message: 'Scraping started',
      data: response.data 
    });
  } catch (error) {
    res.status(500).json({ 
      error: error.message,
      details: error.response?.data 
    });
  }
});

// ==========================================
// SYNC TO SUPABASE
// ==========================================

app.post("/api/sync-to-site", async (req, res) => {
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    const client = new MongoClient(PRIMARY_MONGODB_URI);
    await client.connect();

    const db = client.db("comicktown");
    const { limit = 100 } = req.body;
    const mangaList = await db.collection("manga")
      .find({})
      .limit(limit)
      .toArray();

    let synced = 0;
    let chapters_synced = 0;
    const errors = [];

    for (const manga of mangaList) {
      try {
        const { data: insertedManga, error } = await supabase
          .from("manga")
          .upsert({
            title: manga.title,
            summary: `Imported from ${manga.site}`,
            status: manga.status || "ongoing",
            author: manga.site,
            genres: manga.genres || [manga.site],
            cover_url: manga.cover_image,
            source_url: manga.url,
            rating: 0,
            view_count: 0
          }, { onConflict: 'source_url' })
          .select()
          .single();

        if (error) {
          errors.push(`${manga.title}: ${error.message}`);
          continue;
        }

        synced++;

        const chapters = await db.collection("chapters")
          .find({ manga_url: manga.url })
          .toArray();

        for (const ch of chapters) {
          await supabase.from("chapters").upsert({
            manga_id: insertedManga.id,
            chapter_number: String(ch.number),
            chapter_title: ch.title,
            source_url: ch.url,
            catbox_urls: ch.catbox_images || [],
            page_count: ch.total_images || 0
          }, { onConflict: 'source_url' });
          
          chapters_synced++;
        }

        console.log(`✅ Synced: ${manga.title} (${chapters.length} chapters)`);
      } catch (err) {
        errors.push(`${manga.title}: ${err.message}`);
      }
    }

    await client.close();

    res.json({
      status: "success",
      synced_manga: synced,
      synced_chapters: chapters_synced,
      total_processed: mangaList.length,
      errors: errors
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ==========================================
// STATISTICS
// ==========================================

app.get("/api/stats", async (req, res) => {
  try {
    const client = new MongoClient(PRIMARY_MONGODB_URI);
    await client.connect();
    
    const db = client.db("comicktown");
    
    const [mangaCount, chaptersCount, siteStats] = await Promise.all([
      db.collection("manga").countDocuments(),
      db.collection("chapters").countDocuments(),
      db.collection("manga").aggregate([
        { $group: { _id: "$site", count: { $sum: 1 } } }
      ]).toArray()
    ]);
    
    await client.close();
    
    const bysite = {};
    siteStats.forEach(s => {
      bysite[s._id] = s.count;
    });
    
    res.json({
      total_manga: mangaCount,
      total_chapters: chaptersCount,
      by_site: bysite,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health check
app.get("/health", (req, res) => {
  res.json({ 
    status: "ok", 
    time: new Date().toISOString(),
    version: "2.0.0"
  });
});

// Root
app.get("/", (req, res) => {
  res.json({ 
    name: "Comicktown API v2.0", 
    status: "running",
    sites: ["asura", "comix", "roliascan", "vortexscans", "reaperscans", "stonescape", "omegascans", "allmanga"],
    endpoints: {
      manga: "GET /api/manga?site=asura&limit=50",
      chapters: "GET /api/manga/:mangaUrl/chapters",
      search: "GET /api/search?q=solo+leveling&site=asura",
      latest: "GET /api/latest?limit=20",
      stats: "GET /api/stats",
      scrape: "POST /api/trigger-scrape",
      sync: "POST /api/sync-to-site"
    }
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Comicktown Backend v2.0 running on port ${PORT}`);
  console.log(`📚 Supporting 8 manga sites`);
  console.log(`🔗 Connected to ${MONGODB_URIS.length} MongoDB databases`);
});

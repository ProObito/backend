import express from "express";
import cors from "cors";
import axios from "axios";
import { MongoClient } from "mongodb";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

const MONGODB_URI =
  process.env.MONGODB_URI ||
  "mongodb+srv://wuwamuqo_db_user:NfhgBOs7LeRbSI6S@cluster0.zxqopbx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";

const SUPABASE_URL =
  process.env.SUPABASE_URL ||
  "https://llirkgzjtaqltkxsgazo.supabase.co";

const SUPABASE_KEY =
  process.env.SUPABASE_KEY ||
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsaXJrZ3pqdGFxbHRreHNnYXpvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNDA4ODEsImV4cCI6MjA4MjcxNjg4MX0.z1e8g4GgGy1jQaykQ5AFHR2_kSD11GnsUYyV8t0g3TI";

app.use(cors());
app.use(express.json());

const SERVICES = {
  manga: "https://codewords.agemo.ai/run/manga_scraper_catbox_400bda55",
  batch: "https://codewords.agemo.ai/run/manga_batch_uploader_95bae5eb",
  storage: "https://codewords.agemo.ai/run/mongodb_storage_stats_a3ac1201",
  sync: "https://codewords.agemo.ai/run/mongodb_master_sync_ff22188f"
};

// Import single manga
app.post("/api/manga/import", async (req, res) => {
  try {
    const { source, manga_url, max_chapters } = req.body;
    const response = await axios.post(
      SERVICES.manga,
      {
        mode: "url",
        source,
        manga_url,
        max_chapters: max_chapters || 5
      },
      { timeout: 180000 }
    );
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Sync MongoDB → Supabase
app.post("/api/sync-to-site", async (req, res) => {
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    const client = new MongoClient(MONGODB_URI);
    await client.connect();

    const db = client.db("comicktown");
    const mangaList = await db.collection("manga_imports").find({}).toArray();

    let synced = 0;
    let chapters_synced = 0;
    const errors = [];

    for (const manga of mangaList) {
      try {
        const { data: insertedManga, error } = await supabase
          .from("manga")
          .insert({
            title: manga.title,
            summary: `Imported from ${manga.source}`,
            status: "ongoing",
            author: manga.source,
            genres: [manga.source],
            rating: 0,
            view_count: 0
          })
          .select()
          .single();

        if (error) {
          errors.push(`${manga.title}: ${error.message}`);
          continue;
        }

        synced++;

        for (const ch of manga.chapters || []) {
          await supabase.from("chapters").insert({
            manga_id: insertedManga.id,
            chapter_number: String(ch.num),
            chapter_title: `Chapter ${ch.num}`,
            pdf_url: ch.url,
            page_count: ch.images || 0
          });
          chapters_synced++;
        }

        console.log(`Synced: ${manga.title}`);
      } catch (err) {
        errors.push(`${manga.title}: ${err.message}`);
      }
    }

    await client.close();

    res.json({
      status: "success",
      synced_manga: synced,
      synced_chapters: chapters_synced,
      total: mangaList.length,
      errors
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health
app.get("/health", (req, res) => {
  res.json({ status: "ok", time: new Date().toISOString() });
});

// Root
app.get("/", (req, res) => {
  res.json({ name: "Comicktown API", status: "running" });
});

app.listen(PORT, () => {
  console.log(`🚀 Comicktown Backend running on port ${PORT}`);
});

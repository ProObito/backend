<h2 align="center">
    ──「 𝗖𝗢𝗠𝗜𝗖𝗞𝗧𝗢𝗪𝗡 • 𝗦𝗖𝗥𝗔𝗣𝗘𝗥 𝗘𝗡𝗚𝗜𝗡𝗘 」──
</h2>

<p align="center">
  <img src="https://graph.org/file/386500b2d4b21d5d1f772.jpg">
</p>

<p align="center">
<b>The Automated Backbone of Comicktown</b>
</p>

<p align="center">
Python Powered • Drive Integrated • Multi-Source • High Performance
</p>

---

## 🌐 About Scraper Engine

This is the **Scraper & Automation Backend** for Comicktown. While the main frontend/backend handles user interaction, this engine is responsible for:

- **Automated Scraping**: Fetching the latest Manga/Manhwa from multiple sources.
- **Cloud Storage**: Automatically creating organized folders and uploading images to **Google Drive**.
- **Data Sync**: Pushing updates to the main Comicktown website via API.
- **Source Scalability**: Modular script system to add new sources (RoliaScan, WebCentral, etc.).

---

## 🚀 Scraper Tech Stack

- **Language**: Python 3.10+
- **Framework**: Flask (API Interface)
- **Asynchronous**: `aiohttp` for lightning-fast scraping
- **Parsing**: BeautifulSoup4
- **Cloud API**: Google Drive API v3
- **Deployment**: Optimized for Render / Heroku / VPS

---

## 📂 Project Structure

```text
comicktown-backend/
├── app.py                # Main Entry Point (Flask Server)
├── roliascan.py          # RoliaScan Scraping Logic
├── webcentral.py         # WebCentral Scraping Logic
├── requirements.txt      # Dependencies
├── credentials.json      # Google Service Account Key
├── routes/
│   └── scrape_route.py   # Scraper API Endpoints
├── services/
│   └── drive_service.py  # Google Drive Upload Engine
└── config/
    └── settings.py       # API Keys & Configurations

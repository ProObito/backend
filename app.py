#"""Flask API Server for Manga Scraping"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from orchestrator import MangaOrchestrator
from scrapers import SCRAPERS
import os

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'scrapers': list(SCRAPERS.keys())})

@app.route('/api/scrape/site', methods=['POST'])
def scrape_site():
    """Scrape a single site"""
    data = request.json
    site = data.get('site')
    upload_images = data.get('upload_images', False)
    
    if site not in SCRAPERS:
        return jsonify({'error': f'Invalid site: {site}'}), 400
    
    async def run_scraper():
        orchestrator = MangaOrchestrator()
        await orchestrator.scrape_site(site, upload_images)
        return orchestrator.stats
    
    stats = asyncio.run(run_scraper())
    return jsonify(stats)

@app.route('/api/scrape/all', methods=['POST'])
def scrape_all():
    """Scrape all sites"""
    data = request.json or {}
    upload_images = data.get('upload_images', False)
    
    async def run_all():
        orchestrator = MangaOrchestrator()
        await orchestrator.scrape_all_sites(upload_images=upload_images)
        return orchestrator.stats
    
    stats = asyncio.run(run_all())
    return jsonify(stats)

@app.route('/api/manga/list', methods=['GET'])
def list_manga():
    """List all manga"""
    site = request.args.get('site')
    
    async def get_manga():
        orchestrator = MangaOrchestrator()
        manga = await orchestrator.mongo.get_all_manga(site)
        await orchestrator.mongo.close()
        return manga
    
    manga = asyncio.run(get_manga())
    return jsonify({'manga': manga, 'count': len(manga)})

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'name': 'Comicktown Scraper API',
        'version': '2.0',
        'sites': list(SCRAPERS.keys())
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
  

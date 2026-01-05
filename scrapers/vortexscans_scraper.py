##"""VortexScans - https://vortexscans.org"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper
import json, re

class VortexScansScraper(BaseScraper):
    def __init__(self):
        super().__init__('vortexscans', 'https://vortexscans.org')
    
    async def get_all_manga(self) -> List[Dict]:
        all_manga = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for page in range(1, 100):
                html = await self.fetch_page(f"{self.base_url}/series?page={page}", session)
                if not html: break
                soup = BeautifulSoup(html, 'lxml')
                cards = soup.select('a[href*="/series/"]')
                if not cards: break
                for card in cards:
                    try:
                        title = card.get('title') or card.select_one('h3, h4, .title')
                        title_text = title if isinstance(title, str) else title.get_text(strip=True) if title else ''
                        img = card.select_one('img')
                        manga = {
                            'title': title_text,
                            'url': card['href'] if card['href'].startswith('http') else self.base_url + card['href'],
                            'cover_image': img.get('data-src') or img.get('src') if img else '',
                            'site': self.site_name, 'genres': [], 'status': 'ongoing'
                        }
                        if manga['url'] and manga['title']: all_manga.append(manga)
                    except: continue
                await asyncio.sleep(1)
        return all_manga
    
    async def get_manga_chapters(self, manga_url: str) -> List[Dict]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html = await self.fetch_page(manga_url, session)
            if not html: return []
            soup = BeautifulSoup(html, 'lxml')
            chapters = []
            for link in soup.select('a[href*="/chapter/"], a[href*="/read/"]'):
                try:
                    chapters.append({
                        'title': link.get_text(strip=True),
                        'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                        'number': self.extract_chapter_number(link.get_text()),
                        'release_date': ''
                    })
                except: continue
            return chapters
    
    async def get_chapter_images(self, chapter_url: str) -> List[str]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html = await self.fetch_page(chapter_url, session)
            if not html: return []
            soup = BeautifulSoup(html, 'lxml')
            images = []
            for img in soup.select('#chapter-images img, .reader img'):
                src = img.get('data-src') or img.get('src')
                if src:
                    if not src.startswith('http'): src = self.base_url + src
                    images.append(src.strip())
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'images' in script.string:
                    try:
                        match = re.search(r'images\s*[:=]\s*(\[.*?\])', script.string, re.DOTALL)
                        if match:
                            img_data = json.loads(match.group(1))
                            images.extend([img for img in img_data if isinstance(img, str) and 'http' in img])
                    except: pass
            return list(set(images))

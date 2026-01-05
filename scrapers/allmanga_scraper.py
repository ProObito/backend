#"""AllManga - https://allmanga.to"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper

class AllMangaScraper(BaseScraper):
    def __init__(self):
        super().__init__('allmanga', 'https://allmanga.to')
    
    async def get_all_manga(self) -> List[Dict]:
        all_manga = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for page in range(1, 200):
                html = await self.fetch_page(f"{self.base_url}/browse?page={page}", session)
                if not html: break
                soup = BeautifulSoup(html, 'lxml')
                links = soup.select('a[href*="/manga/"]')
                if not links: break
                for link in links:
                    try:
                        title = link.get('title') or link.get_text(strip=True)
                        img = link.select_one('img')
                        manga = {
                            'title': title,
                            'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                            'cover_image': img.get('data-src') or img.get('src') if img else '',
                            'site': self.site_name, 'genres': [], 'status': 'ongoing'
                        }
                        if manga['url'] and manga['title']: all_manga.append(manga)
                    except: continue
                await asyncio.sleep(1)
        return list({m['url']: m for m in all_manga}.values())
    
    async def get_manga_chapters(self, manga_url: str) -> List[Dict]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html = await self.fetch_page(manga_url, session)
            if not html: return []
            soup = BeautifulSoup(html, 'lxml')
            chapters = []
            for link in soup.select('a[href*="/chapter-"]'):
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
            for img in soup.select('.reader img, .chapter-images img'):
                src = img.get('data-src') or img.get('src')
                if src and 'http' in src: images.append(src.strip())
            return images
          

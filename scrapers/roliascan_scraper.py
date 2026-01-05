##"""RoliaScan - https://roliascan.com"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper

class RoliaScanScraper(BaseScraper):
    def __init__(self):
        super().__init__('roliascan', 'https://roliascan.com')
    
    async def get_all_manga(self) -> List[Dict]:
        all_manga = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for page in range(1, 50):
                html = await self.fetch_page(f"{self.base_url}/manga?page={page}", session)
                if not html or 'not found' in html.lower(): break
                soup = BeautifulSoup(html, 'lxml')
                items = soup.select('.page-item-detail, .manga-item')
                if not items: break
                for item in items:
                    try:
                        link = item.select_one('a[href*="/manga/"]')
                        if not link: continue
                        title_elem = item.select_one('.post-title h3, .tt') or link
                        img = item.select_one('img')
                        manga = {
                            'title': title_elem.get_text(strip=True),
                            'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                            'cover_image': img.get('data-src') or img.get('src') if img else '',
                            'site': self.site_name, 'genres': [], 'status': 'ongoing'
                        }
                        if manga['url'] and manga['title']: all_manga.append(manga)
                    except: continue
                await asyncio.sleep(1.5)
        return all_manga
    
    async def get_manga_chapters(self, manga_url: str) -> List[Dict]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html = await self.fetch_page(manga_url, session)
            if not html: return []
            soup = BeautifulSoup(html, 'lxml')
            chapters = []
            for link in soup.select('.wp-manga-chapter a, a[href*="/chapter/"]'):
                try:
                    chapters.append({
                        'title': link.get_text(strip=True),
                        'url': link['href'],
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
            for img in soup.select('.reading-content img, #readerarea img'):
                src = img.get('data-src') or img.get('src')
                if src and 'http' in src: images.append(src.strip())
            return images

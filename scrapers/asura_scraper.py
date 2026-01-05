#"""AsuraScans Scraper https://asuracomic.net """
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper

class AsuraScraper(BaseScraper):
    def __init__(self):
        super().__init__('asura', 'https://asuracomic.net')
    
    async def get_all_manga(self) -> List[Dict]:
        """Get all manga from AsuraScans"""
        all_manga = []
        page = 1
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            while True:
                url = f"{self.base_url}/series?page={page}"
                html = await self.fetch_page(url, session)
                
                if not html:
                    break
                
                soup = BeautifulSoup(html, 'lxml')
                manga_items = soup.select('div[class*="series"], div.bsx, a[href*="/series/"]')
                
                if not manga_items:
                    break
                
                for item in manga_items:
                    try:
                        link = item if item.name == 'a' else item.select_one('a[href*="/series/"]')
                        if not link or not link.get('href'):
                            continue
                        
                        title_elem = link.select_one('.tt, .bigor, h2, h3') or link
                        img_elem = item.select_one('img')
                        
                        manga = {
                            'title': title_elem.get_text(strip=True),
                            'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                            'cover_image': img_elem.get('data-src') or img_elem.get('src') if img_elem else '',
                            'site': self.site_name,
                            'genres': [],
                            'status': 'ongoing'
                        }
                        
                        if manga['url'] and manga['title']:
                            all_manga.append(manga)
                    except Exception as e:
                        continue
                
                page += 1
                await asyncio.sleep(1)
        
        return all_manga
    
    async def get_manga_chapters(self, manga_url: str) -> List[Dict]:
        """Get all chapters for a manga"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html = await self.fetch_page(manga_url, session)
            
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'lxml')
            chapters = []
            
            chapter_links = soup.select('div.eplister a, div.chbox a, a[href*="/chapter/"]')
            
            for link in chapter_links:
                try:
                    chapter = {
                        'title': link.get_text(strip=True),
                        'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                        'number': self.extract_chapter_number(link.get_text()),
                        'release_date': ''
                    }
                    
                    # Try to get release date
                    date_elem = link.find_next('span', class_='chapterdate')
                    if date_elem:
                        chapter['release_date'] = date_elem.get_text(strip=True)
                    
                    chapters.append(chapter)
                except Exception as e:
                    continue
            
            return chapters
    
    async def get_chapter_images(self, chapter_url: str) -> List[str]:
        """Get all images from a chapter"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html = await self.fetch_page(chapter_url, session)
            
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'lxml')
            images = []
            
            # AsuraScans uses different reader formats
            img_elements = soup.select('#readerarea img, .rdminimal img, .reader-area img')
            
            for img in img_elements:
                src = img.get('data-src') or img.get('src')
                if src and 'http' in src:
                    images.append(src.strip())
            
            return images 

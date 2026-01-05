##"""Comix.to Scraper https://comix.to """
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper
import json
import re

class ComixScraper(BaseScraper):
    def __init__(self):
        super().__init__('comix', 'https://comix.to')
    
    async def get_all_manga(self) -> List[Dict]:
        """Get all manga from Comix.to"""
        all_manga = []
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Comix.to has browse/search pages
            url = f"{self.base_url}/browse"
            html = await self.fetch_page(url, session)
            
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Find all manga links
            manga_links = soup.select('a[href*="/title/"]')
            
            for link in manga_links:
                try:
                    title = link.get('title') or link.get_text(strip=True)
                    href = link['href']
                    
                    img = link.select_one('img')
                    
                    manga = {
                        'title': title,
                        'url': href if href.startswith('http') else self.base_url + href,
                        'cover_image': img.get('data-src') or img.get('src') if img else '',
                        'site': self.site_name,
                        'genres': [],
                        'status': 'ongoing'
                    }
                    
                    if manga['url'] and manga['title']:
                        all_manga.append(manga)
                except Exception as e:
                    continue
            
            await asyncio.sleep(1)
        
        return list({m['url']: m for m in all_manga}.values())  # Remove duplicates
    
    async def get_manga_chapters(self, manga_url: str) -> List[Dict]:
        """Get all chapters"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html = await self.fetch_page(manga_url, session)
            
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'lxml')
            chapters = []
            
            chapter_links = soup.select('a[href*="/chapter-"]')
            
            for link in chapter_links:
                try:
                    chapter = {
                        'title': link.get_text(strip=True),
                        'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                        'number': self.extract_chapter_number(link.get_text()),
                        'release_date': ''
                    }
                    chapters.append(chapter)
                except Exception as e:
                    continue
            
            return chapters
    
    async def get_chapter_images(self, chapter_url: str) -> List[str]:
        """Get chapter images"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            html = await self.fetch_page(chapter_url, session)
            
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'lxml')
            images = []
            
            # Look for image container
            img_elements = soup.select('.chapter-images img, #chapter-reader img')
            
            for img in img_elements:
                src = img.get('data-src') or img.get('src')
                if src:
                    images.append(src.strip())
            
            # Also check for JSON data in scripts
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'images' in script.string:
                    try:
                        match = re.search(r'images\s*[:=]\s*(\[.*?\])', script.string, re.DOTALL)
                        if match:
                            img_data = json.loads(match.group(1))
                            images.extend([img for img in img_data if isinstance(img, str)])
                    except:
                        pass
            
            return list(set(images))

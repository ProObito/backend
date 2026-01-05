#Base Scraper Class - All scrapers inherit from this
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Dict
import re

class BaseScraper(ABC):
    def __init__(self, site_name: str, base_url: str):
        self.site_name = site_name
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
    
    @abstractmethod
    async def get_all_manga(self) -> List[Dict]:
        """Get all manga from site"""
        pass
    
    @abstractmethod
    async def get_manga_chapters(self, manga_url: str) -> List[Dict]:
        """Get all chapters for a manga"""
        pass
    
    @abstractmethod
    async def get_chapter_images(self, chapter_url: str) -> List[str]:
        """Get all image URLs from chapter"""
        pass
    
    def extract_chapter_number(self, text: str) -> str:
        """Extract chapter number from text"""
        patterns = [
            r'Chapter\s+(\d+(?:\.\d+)?)',
            r'Ch\.?\s+(\d+(?:\.\d+)?)',
            r'#(\d+(?:\.\d+)?)',
            r'Episode\s+(\d+(?:\.\d+)?)',
            r'Ep\.?\s+(\d+(?:\.\d+)?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return '0'
    
    async def fetch_page(self, url: str, session: aiohttp.ClientSession = None) -> str:
        """Fetch page with error handling"""
        close_session = False
        if session is None:
            session = aiohttp.ClientSession(headers=self.headers)
            close_session = True
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.text()
                return ""
        except Exception as e:
            print(f"❌ Fetch error {url}: {str(e)}")
            return ""
        finally:
            if close_session:
                await session.close()

#"""
#RoliaScan Scraper
#Scrapes all manga and chapters from roliascan.com
#"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import re

class RoliaScanScraper:
    def __init__(self):
        self.base_url = "https://roliascan.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def get_all_manga(self) -> List[Dict]:
        """Get all manga from the site"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # RoliaScan uses pagination
            all_manga = []
            page = 1
            
            while True:
                url = f"{self.base_url}/manga?page={page}"
                async with session.get(url) as response:
                    if response.status != 200:
                        break
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find manga items (adjust selectors based on actual site)
                    manga_items = soup.select('.page-item-detail')
                    
                    if not manga_items:
                        break
                    
                    for item in manga_items:
                        try:
                            title_elem = item.select_one('.post-title h3 a')
                            img_elem = item.select_one('img.img-responsive')
                            
                            manga = {
                                'title': title_elem.text.strip() if title_elem else '',
                                'url': title_elem['href'] if title_elem else '',
                                'cover_image': img_elem['data-src'] if img_elem and 'data-src' in img_elem.attrs else img_elem['src'] if img_elem else '',
                                'site': 'roliascan'
                            }
                            
                            if manga['url']:
                                all_manga.append(manga)
                        except Exception as e:
                            print(f"Error parsing manga item: {e}")
                            continue
                    
                    page += 1
                    await asyncio.sleep(1)  # Rate limiting
            
            return all_manga
    
    async def get_manga_chapters(self, manga_url: str) -> List[Dict]:
        """Get all chapters for a specific manga"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(manga_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                chapters = []
                chapter_items = soup.select('.wp-manga-chapter a')
                
                for item in chapter_items:
                    try:
                        chapter = {
                            'title': item.text.strip(),
                            'url': item['href'],
                            'number': self._extract_chapter_number(item.text)
                        }
                        chapters.append(chapter)
                    except Exception as e:
                        print(f"Error parsing chapter: {e}")
                        continue
                
                return chapters
    
    async def get_chapter_images(self, chapter_url: str) -> List[str]:
        """Get all image URLs from a chapter"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(chapter_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                images = []
                img_elements = soup.select('.reading-content img')
                
                for img in img_elements:
                    src = img.get('data-src') or img.get('src')
                    if src and src.startswith('http'):
                        images.append(src.strip())
                
                return images
    
    def _extract_chapter_number(self, text: str) -> str:
        """Extract chapter number from text"""
        match = re.search(r'Chapter\s+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        return match.group(1) if match else '0'


# Test function
async def test_roliascan():
    scraper = RoliaScanScraper()
    
    print("🔍 Testing RoliaScan Scraper...")
    manga_list = await scraper.get_all_manga()
    print(f"✅ Found {len(manga_list)} manga")
    
    if manga_list:
        first_manga = manga_list[0]
        print(f"\n📖 Testing: {first_manga['title']}")
        chapters = await scraper.get_manga_chapters(first_manga['url'])
        print(f"✅ Found {len(chapters)} chapters")
        
        if chapters:
            images = await scraper.get_chapter_images(chapters[0]['url'])
            print(f"✅ Found {len(images)} images in first chapter")

if __name__ == "__main__":
    asyncio.run(test_roliascan())
                    
                    

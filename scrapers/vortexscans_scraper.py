"""
VortexScans Scraper
Scrapes all manga from vortexscans.org
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import json
import re

class VortexScansScraper:
    def __init__(self):
        self.base_url = "https://vortexscans.org"
        self.api_url = "https://vortexscans.org/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
    
    async def get_all_manga(self) -> List[Dict]:
        """Get all manga from VortexScans"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            all_manga = []
            page = 1
            
            while True:
                # VortexScans might use API or HTML
                url = f"{self.base_url}/series?page={page}"
                
                async with session.get(url) as response:
                    if response.status != 200:
                        break
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find manga cards (adjust based on actual HTML structure)
                    manga_cards = soup.select('.series-card, .manga-item, [class*="series"]')
                    
                    if not manga_cards:
                        break
                    
                    for card in manga_cards:
                        try:
                            title_elem = card.select_one('a[href*="/series/"]')
                            img_elem = card.select_one('img')
                            
                            if not title_elem:
                                continue
                            
                            manga = {
                                'title': title_elem.get('title', '') or card.select_one('.title, h3, h4').text.strip() if card.select_one('.title, h3, h4') else '',
                                'url': title_elem['href'] if title_elem['href'].startswith('http') else self.base_url + title_elem['href'],
                                'cover_image': img_elem['src'] if img_elem else '',
                                'site': 'vortexscans'
                            }
                            
                            if manga['url']:
                                all_manga.append(manga)
                        except Exception as e:
                            print(f"Error parsing manga: {e}")
                            continue
                    
                    page += 1
                    await asyncio.sleep(1)
            
            return all_manga
    
    async def get_manga_chapters(self, manga_url: str) -> List[Dict]:
        """Get all chapters for a manga"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(manga_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                chapters = []
                chapter_links = soup.select('a[href*="/chapter/"], a[href*="/read/"]')
                
                for link in chapter_links:
                    try:
                        chapter = {
                            'title': link.text.strip(),
                            'url': link['href'] if link['href'].startswith('http') else self.base_url + link['href'],
                            'number': self._extract_chapter_number(link.text)
                        }
                        chapters.append(chapter)
                    except Exception as e:
                        continue
                
                return chapters
    
    async def get_chapter_images(self, chapter_url: str) -> List[str]:
        """Get all images from a chapter"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(chapter_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                images = []
                
                # Try to find images in reader
                img_elements = soup.select('#chapter-images img, .chapter-content img, .reader img')
                
                for img in img_elements:
                    src = img.get('data-src') or img.get('src')
                    if src:
                        if not src.startswith('http'):
                            src = self.base_url + src
                        images.append(src.strip())
                
                # Also try to find data-images JSON
                script_tags = soup.find_all('script')
                for script in script_tags:
                    if script.string and 'images' in script.string:
                        try:
                            # Extract JSON data
                            match = re.search(r'images\s*[:=]\s*(\[.*?\])', script.string, re.DOTALL)
                            if match:
                                img_data = json.loads(match.group(1))
                                images.extend([img for img in img_data if isinstance(img, str)])
                        except:
                            pass
                
                return list(set(images))  # Remove duplicates
    
    def _extract_chapter_number(self, text: str) -> str:
        match = re.search(r'(?:Chapter|Ch\.?)\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        return match.group(1) if match else '0'

# Test
async def test_vortex():
    scraper = VortexScansScraper()
    print("🔍 Testing VortexScans...")
    manga = await scraper.get_all_manga()
    print(f"✅ Found {len(manga)} manga")

if __name__ == "__main__":
    asyncio.run(test_vortex())

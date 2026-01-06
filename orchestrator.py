#""" Main Orchestrator - Scrapes all sites and uploads ho"""
import asyncio
from scrapers import SCRAPERS
from utils import CatboxUploader, DriveUploader, MongoHandler
import os
from datetime import datetime
import json

class MangaOrchestrator:
    def __init__(self):
        # MongoDB URIs
        self.mongo_uris = [
            os.getenv('MONGODB_URI_1', 'mongodb+srv://probito140:umaid2008@cluster0.1utfc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'),
            os.getenv('MONGODB_URI_2', 'mongodb+srv://wuwamuqo_db_user:NfhgBOs7LeRbSI6S@cluster0.zxqopbx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'),
            os.getenv('MONGODB_URI_3', 'mongodb+srv://spxsolo:umaid2008@cluster0.7fbux.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        ]
        
        self.catbox = CatboxUploader(os.getenv('CATBOX_USERHASH', 'd1ed339a018c4d26402c8b75f'))
        self.drive = DriveUploader(os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT', '{}'))
        self.mongo = MongoHandler(self.mongo_uris)
        
        self.stats = {
            'total_manga': 0,
            'total_chapters': 0,
            'images_uploaded': 0,
            'errors': []
        }
    
    async def scrape_site(self, site_name: str, upload_images: bool = True):
        """Scrape a complete site"""
        print(f"\n🚀 Starting {site_name.upper()} scraper...")
        
        try:
            scraper_class = SCRAPERS.get(site_name)
            if not scraper_class:
                print(f"❌ Scraper not found: {site_name}")
                return
            
            scraper = scraper_class()
            
            # Get all manga
            print(f"📚 Fetching manga list from {site_name}...")
            manga_list = await scraper.get_all_manga()
            print(f"✅ Found {len(manga_list)} manga on {site_name}")
            
            self.stats['total_manga'] += len(manga_list)
            
            # Process each manga
            for idx, manga in enumerate(manga_list, 1):
                try:
                    print(f"\n[{idx}/{len(manga_list)}] Processing: {manga['title']}")
                    
                    # Save manga metadata
                    await self.mongo.save_manga(manga)
                    
                    # Get chapters
                    chapters = await scraper.get_manga_chapters(manga['url'])
                    print(f"  📖 Found {len(chapters)} chapters")
                    
                    self.stats['total_chapters'] += len(chapters)
                    
                    # Process chapters
                    for ch_idx, chapter in enumerate(chapters[:5], 1):  # Limit to 5 per manga for testing
                        try:
                            print(f"    [{ch_idx}/{len(chapters)}] Chapter {chapter['number']}...")
                            
                            if upload_images:
                                # Get chapter images
                                images = await scraper.get_chapter_images(chapter['url'])
                                print(f"      🖼️  Found {len(images)} images")
                                
                                if images:
                                    # Upload first image as test
                                    catbox_url = await self.catbox.upload_from_url(
                                        images[0],
                                        f"{site_name}_{manga['title']}_{chapter['number']}_p1.jpg"
                                    )
                                    
                                    chapter['catbox_images'] = [catbox_url] if catbox_url else []
                                    chapter['total_images'] = len(images)
                                    chapter['image_urls'] = images  # Save original URLs
                                    
                                    self.stats['images_uploaded'] += 1
                            
                            # Save chapter
                            chapter['manga_title'] = manga['title']
                            chapter['manga_url'] = manga['url']
                            await self.mongo.save_chapter(chapter)
                            
                        except Exception as e:
                            print(f"      ❌ Chapter error: {str(e)}")
                            self.stats['errors'].append(f"{manga['title']} Ch{chapter['number']}: {str(e)}")
                    
                    await asyncio.sleep(2)  # Rate limiting between manga
                    
                except Exception as e:
                    print(f"  ❌ Manga error: {str(e)}")
                    self.stats['errors'].append(f"{manga['title']}: {str(e)}")
        
        except Exception as e:
            print(f"❌ Site scraper error {site_name}: {str(e)}")
            self.stats['errors'].append(f"{site_name}: {str(e)}")
    
    async def scrape_all_sites(self, sites: List[str] = None, upload_images: bool = True):
        """Scrape multiple sites"""
        sites_to_scrape = sites or list(SCRAPERS.keys())
        
        print(f"🎯 Scraping {len(sites_to_scrape)} sites: {', '.join(sites_to_scrape)}")
        
        for site in sites_to_scrape:
            await self.scrape_site(site, upload_images)
        
        await self.mongo.close()
        
        print("\n" + "="*60)
        print("📊 FINAL STATS")
        print("="*60)
        print(f"Total Manga: {self.stats['total_manga']}")
        print(f"Total Chapters: {self.stats['total_chapters']}")
        print(f"Images Uploaded: {self.stats['images_uploaded']}")
        print(f"Errors: {len(self.stats['errors'])}")
        print("="*60)

# CLI Entry Point
async def main():
    orchestrator = MangaOrchestrator()
    await orchestrator.scrape_all_sites(upload_images=False)  # Set True to upload images

if __name__ == "__main__":
    asyncio.run(main())

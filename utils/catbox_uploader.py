"""
Catbox.moe Uploader
"""
import aiohttp
import asyncio
from typing import Optional

class CatboxUploader:
    def __init__(self, userhash: str):
        self.userhash = userhash
        self.api_url = "https://catbox.moe/user/api.php"
    
    async def upload_from_url(self, image_url: str, filename: str) -> Optional[str]:
        """Upload image from URL to Catbox"""
        try:
            async with aiohttp.ClientSession() as session:
                # Download image
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        print(f"❌ Failed to download {image_url}")
                        return None
                    
                    image_data = await response.read()
                
                # Upload to Catbox
                form = aiohttp.FormData()
                form.add_field('reqtype', 'fileupload')
                form.add_field('userhash', self.userhash)
                form.add_field('fileToUpload', image_data, filename=filename, content_type='image/jpeg')
                
                async with session.post(self.api_url, data=form, timeout=aiohttp.ClientTimeout(total=60)) as upload_response:
                    if upload_response.status == 200:
                        catbox_url = await upload_response.text()
                        catbox_url = catbox_url.strip()
                        print(f"✅ Catbox: {catbox_url}")
                        return catbox_url
                    else:
                        print(f"❌ Catbox upload failed: {upload_response.status}")
                        return None
        except Exception as e:
            print(f"❌ Catbox error: {str(e)}")
            return None
    
    async def upload_multiple(self, images: list[tuple[str, str]]) -> list[str]:
        """Upload multiple images (url, filename)"""
        tasks = [self.upload_from_url(url, filename) for url, filename in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if r and not isinstance(r, Exception)]
#FILE 13: utils/drive_uploader.py

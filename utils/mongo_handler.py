"""MongoDB Handler - Saves to all 3 databases"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional
import asyncio
from datetime import datetime

class MongoHandler:
    def __init__(self, uris: List[str]):
        self.uris = uris
        self.clients = [AsyncIOMotorClient(uri) for uri in uris]
        self.db_name = 'comicktown'
    
    async def save_manga(self, manga_data: Dict) -> bool:
        """Save manga to all databases"""
        manga_data['created_at'] = datetime.now()
        manga_data['updated_at'] = datetime.now()
        
        tasks = []
        for client in self.clients:
            db = client[self.db_name]
            collection = db['manga']
            # Upsert based on URL
            task = collection.update_one(
                {'url': manga_data['url']},
                {'$set': manga_data},
                upsert=True
            )
            tasks.append(task)
        
        try:
            await asyncio.gather(*tasks)
            return True
        except Exception as e:
            print(f"❌ MongoDB save error: {str(e)}")
            return False
    
    async def save_chapter(self, chapter_data: Dict) -> bool:
        """Save chapter to all databases"""
        chapter_data['created_at'] = datetime.now()
        chapter_data['updated_at'] = datetime.now()
        
        tasks = []
        for client in self.clients:
            db = client[self.db_name]
            collection = db['chapters']
            task = collection.update_one(
                {'url': chapter_data['url']},
                {'$set': chapter_data},
                upsert=True
            )
            tasks.append(task)
        
        try:
            await asyncio.gather(*tasks)
            return True
        except Exception as e:
            print(f"❌ Chapter save error: {str(e)}")
            return False
    
    async def get_all_manga(self, site: Optional[str] = None) -> List[Dict]:
        """Get all manga from primary database"""
        try:
            db = self.clients[0][self.db_name]
            collection = db['manga']
            query = {'site': site} if site else {}
            cursor = collection.find(query)
            return await cursor.to_list(length=10000)
        except Exception as e:
            print(f"❌ MongoDB read error: {str(e)}")
            return []
    
    async def close(self):
        """Close all connections"""
        for client in self.clients:
            client.close()

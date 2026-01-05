#""" Configuration for Comicktown Backend """
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB URIs (all 3 databases)
    MONGODB_URIS = [
        os.getenv('MONGODB_URI_1', 'mongodb+srv://probito140:umaid2008@cluster0.1utfc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'),
        os.getenv('MONGODB_URI_2', 'mongodb+srv://wuwamuqo_db_user:NfhgBOs7LeRbSI6S@cluster0.zxqopbx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'),
        os.getenv('MONGODB_URI_3', 'mongodb+srv://spxsolo:umaid2008@cluster0.7fbux.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    ]
    
    # Catbox
    CATBOX_USERHASH = os.getenv('CATBOX_USERHASH', 'd1ed339a018c4d26402c8b75f')
    
    # Google Drive Service Account (JSON string)
    GOOGLE_DRIVE_CREDENTIALS = os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT', '')
    
    # Database name
    DB_NAME = 'comicktown'
    
    # Collections
    MANGA_COLLECTION = 'manga'
    CHAPTERS_COLLECTION = 'chapters'
    IMAGES_COLLECTION = 'images'
    
    # Rate limiting
    SCRAPE_DELAY = 1  # seconds between requests
    MAX_CONCURRENT = 5  # max parallel scrapers
    
    # Scheduling
    SCRAPE_INTERVAL_HOURS = 1  # Run every hour
    
    # Sites to scrape
    ENABLED_SITES = [
        'asura',
        'comix',
        'roliascan',
        'vortexscans',
        'reaperscans',
        'stonescape',
        'omegascans',
        'allmanga'
    ]

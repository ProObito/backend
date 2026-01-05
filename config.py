#"""Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB URIs (all 3)
    MONGODB_URIS = [
        os.getenv('MONGODB_URI_1', 'mongodb+srv://probito140:umaid2008@cluster0.1utfc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'),
        os.getenv('MONGODB_URI_2', 'mongodb+srv://wuwamuqo_db_user:NfhgBOs7LeRbSI6S@cluster0.zxqopbx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'),
        os.getenv('MONGODB_URI_3', 'mongodb+srv://spxsolo:umaid2008@cluster0.7fbux.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    ]
    
    CATBOX_USERHASH = os.getenv('CATBOX_USERHASH', 'd1ed339a018c4d26402c8b75f')
    GOOGLE_DRIVE_SERVICE_ACCOUNT = os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT', '')
    
    DB_NAME = 'comicktown'
    SCRAPE_DELAY = 1
    MAX_CONCURRENT = 5
    SCRAPE_INTERVAL_HOURS = 1
    
    ENABLED_SITES = ['asura', 'comix', 'roliascan', 'vortexscans', 'reaperscans', 'stonescape', 'omegascans', 'allmanga']
    

#"""Google Drive Uploader with Multi-Account Support"""
import asyncio
import aiohttp
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from typing import Optional, List

class DriveUploader:
    def __init__(self, credentials_json: str, drive_accounts: List[str] = None):
        """
        credentials_json: JSON string of service account
        drive_accounts: List of 5 service account JSONs for rotation
        """
        self.credentials = json.loads(credentials_json)
        self.drive_accounts = drive_accounts or [credentials_json]
        self.current_account_index = 0
    
    def _get_drive_service(self):
        """Get Google Drive service with current account"""
        creds_json = json.loads(self.drive_accounts[self.current_account_index])
        credentials = service_account.Credentials.from_service_account_info(creds_json)
        return build('drive', 'v3', credentials=credentials)
    
    def _rotate_account(self):
        """Rotate to next Drive account"""
        self.current_account_index = (self.current_account_index + 1) % len(self.drive_accounts)
        print(f"🔄 Rotated to Drive account {self.current_account_index + 1}")
    
    async def upload_from_url(self, image_url: str, filename: str, folder_id: Optional[str] = None) -> Optional[str]:
        """Upload image from URL to Google Drive"""
        try:
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return None
                    image_data = await response.read()
            
            # Upload to Drive
            service = self._get_drive_service()
            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaInMemoryUpload(image_data, mimetype='image/jpeg', resumable=True)
            
            file = await asyncio.to_thread(
                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,webViewLink'
                ).execute
            )
            
            drive_url = file.get('webViewLink', '')
            print(f"✅ Drive: {drive_url}")
            return drive_url
            
        except Exception as e:
            print(f"❌ Drive error: {str(e)}")
            # Try rotating account on error
            self._rotate_account()
            return None
    
    async def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Create folder in Drive"""
        try:
            service = self._get_drive_service()
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = await asyncio.to_thread(
                service.files().create(body=file_metadata, fields='id').execute
            )
            
            return folder.get('id')
        except Exception as e:
            print(f"❌ Folder creation error: {str(e)}")
            return None
          

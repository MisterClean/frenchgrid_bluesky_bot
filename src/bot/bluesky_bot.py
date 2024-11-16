import os
import logging
from typing import Dict, Optional
from atproto import Client
from datetime import datetime

logger = logging.getLogger(__name__)

class BlueskyBot:
    def __init__(self):
        self.handle = os.getenv("BLUESKY_HANDLE")
        self.password = os.getenv("BLUESKY_PASSWORD")
        
        if not all([self.handle, self.password]):
            raise ValueError("BLUESKY_HANDLE and BLUESKY_PASSWORD must be set")
        
        self.client = Client()
        self._login()
    
    def _login(self):
        """Login to Bluesky."""
        try:
            self.client.login(self.handle, self.password)
            logger.info("Successfully logged into Bluesky")
        except Exception as e:
            logger.error(f"Failed to login to Bluesky: {str(e)}")
            raise

    def create_post(self, text: str):
        """Create a new post on Bluesky."""
        try:
            self.client.send_post(text=text)
            logger.info("Successfully posted to Bluesky")
            
            if os.getenv("SAVE_POSTS", "false").lower() == "true":
                self._save_post(text)
                
        except Exception as e:
            logger.error(f"Failed to post to Bluesky: {str(e)}")
            raise

    def _save_post(self, text: str):
        """Save post to a local file if SAVE_POSTS is enabled."""
        try:
            with open("posts.log", "a") as f:
                timestamp = datetime.utcnow().isoformat()
                f.write(f"[{timestamp}] {text}\n\n")
        except Exception as e:
            logger.error(f"Failed to save post: {str(e)}")

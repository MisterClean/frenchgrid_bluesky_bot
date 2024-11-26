import os
import logging
import time
import httpx
import yaml
from atproto import Client
from typing import Dict, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class BlueskyBot:
    def __init__(self, max_retries: int = 5, initial_delay: int = 10):
        # Load config
        self._load_config()

        self.handle = os.getenv("BLUESKY_HANDLE")
        self.password = os.getenv("BLUESKY_PASSWORD")

        if not all([self.handle, self.password]):
            raise ValueError("BLUESKY_HANDLE and BLUESKY_PASSWORD must be set")

        self.client = Client()
        self.max_retries = max_retries
        self.initial_delay = initial_delay

        # Try to log in with exponential backoff
        self._login_with_retries()

    def _load_config(self):
        """Load configuration from yaml file."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            raise

    def _login_with_retries(self):
        retries = 0
        delay = self.initial_delay
        while retries < self.max_retries:
            try:
                self.client.login(self.handle, self.password)
                logger.info("Logged in successfully!")
                return  # Exit if login is successful
            except Exception as e:
                logger.error(f"Login attempt {retries + 1} failed: {e}")
                if "RateLimitExceeded" in str(e) or "validation errors" in str(e):
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    retries += 1
                else:
                    raise e
        raise Exception("Max retries exceeded. Could not log in to Bluesky.")

    def create_post(self, text: str):
        """Create a new post on Bluesky with a link to ElectricityMaps."""
        try:
            # Find byte indices for the link text
            link_text = "Electricity Maps"
            byte_text = text.encode('utf-8')
            text_pos = text.find(link_text)
            
            if text_pos == -1:
                raise ValueError(f"Could not find '{link_text}' in text: {text}")
                
            # Calculate byte positions
            byte_start = len(text[:text_pos].encode('utf-8'))
            byte_end = byte_start + len(link_text.encode('utf-8'))
            
            # Create facet for the link
            facets = [{
                'index': {
                    'byteStart': byte_start,
                    'byteEnd': byte_end
                },
                'features': [{
                    '$type': 'app.bsky.richtext.facet#link',
                    'uri': 'https://app.electricitymaps.com/'
                }]
            }]

            # Create the post record
            record = {
                'text': text,
                'facets': facets,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                '$type': 'app.bsky.feed.post'
            }

            # Create the post with proper data structure
            data = {
                'collection': 'app.bsky.feed.post',
                'repo': self.client.me.did,
                'record': record
            }

            # Send the post
            self.client.com.atproto.repo.create_record(data=data)
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
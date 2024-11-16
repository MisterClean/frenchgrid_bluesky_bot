import os
import logging
import time
from atproto import Client
from typing import Optional

logger = logging.getLogger(__name__)

class BlueskyBot:
    def __init__(self, max_retries: int = 5, initial_delay: int = 10):
        self.handle = os.getenv("BLUESKY_HANDLE")
        self.password = os.getenv("BLUESKY_PASSWORD")

        if not all([self.handle, self.password]):
            raise ValueError("BLUESKY_HANDLE and BLUESKY_PASSWORD must be set")

        self.client = Client()
        self.max_retries = max_retries
        self.initial_delay = initial_delay

        # Try to log in with exponential backoff
        self._login_with_retries()

    def _login_with_retries(self):
        retries = 0
        delay = self.initial_delay
        while retries < self.max_retries:
            try:
                response = self.client.login(self.handle, self.password)
                logger.info("Logged in successfully!")
                return
            except Exception as e:
                logger.error(f"Login attempt {retries + 1} failed: {e}")
                # Add debugging to log the response content if possible
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Response content: {e.response.content}")
                if "RateLimitExceeded" in str(e):
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    retries += 1
                else:
                    raise e
        raise Exception("Max retries exceeded. Could not log in to Bluesky.")

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

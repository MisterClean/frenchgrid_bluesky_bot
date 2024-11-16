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
                self.account_tag = config.get("account_tag", "@electricitymaps.bsky.social")
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

    def resolve_handle_to_did(self, handle: str) -> Optional[str]:
        """Resolve a Bluesky handle to its DID."""
        clean_handle = handle.lstrip("@")
        try:
            response = httpx.get(
                "https://bsky.social/xrpc/com.atproto.identity.resolveHandle",
                params={"handle": clean_handle},
            )
            response.raise_for_status()
            return response.json().get("did")
        except httpx.RequestError as e:
            logger.error(f"Error resolving handle '{handle}': {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when resolving handle '{handle}': {str(e)}")
            return None

    def create_post(self, text: str):
        """Create a new post on Bluesky with mention."""
        try:
            # Resolve the DID of the account tag from config.yaml
            did = self.resolve_handle_to_did(self.account_tag)
            if not did:
                logger.error(f"Failed to resolve DID for handle: {self.account_tag}")
                return

            # Encode text to bytes and calculate byte positions for the mention
            text_bytes = text.encode("utf-8")
            mention_bytes = self.account_tag.encode("utf-8")

            mention_start = text_bytes.find(mention_bytes)
            mention_end = mention_start + len(mention_bytes)

            # Create facet for mention using byte positions
            facets = [
                {
                    "index": {
                        "byteStart": mention_start,
                        "byteEnd": mention_end,
                    },
                    "features": [
                        {
                            "$type": "app.bsky.richtext.facet#mention",
                            "did": did,
                        }
                    ],
                }
            ]

            # Send the post using the correct parameters
            self.client.send_post(
                text=text,
                facets=facets
            )
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

"""
Configuration management for the French Grid Bluesky Bot.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    # Bluesky credentials
    BLUESKY_HANDLE: str = os.getenv('BLUESKY_HANDLE', '')
    BLUESKY_PASSWORD: str = os.getenv('BLUESKY_PASSWORD', '')
    
    # API configuration
    API_IP: Optional[str] = os.getenv('API_IP')
    API_PORT: Optional[str] = os.getenv('API_PORT')
    
    # Features
    SAVE_POSTS: bool = os.getenv('SAVE_POSTS', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration settings.
        
        Raises:
            ValueError: If any required settings are missing
        """
        if not cls.BLUESKY_HANDLE or not cls.BLUESKY_PASSWORD:
            raise ValueError(
                "Missing Bluesky credentials. Please set BLUESKY_HANDLE and "
                "BLUESKY_PASSWORD in your .env file"
            )
        
        if cls.SAVE_POSTS and (not cls.API_IP or not cls.API_PORT):
            raise ValueError(
                "API configuration is required when SAVE_POSTS is enabled. "
                "Please set API_IP and API_PORT in your .env file"
            )

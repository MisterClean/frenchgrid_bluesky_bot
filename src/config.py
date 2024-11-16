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
    
    # Electricity Maps API
    ELECTRICITY_MAPS_TOKEN: str = os.getenv('ELECTRICITY_MAPS_TOKEN', '')
    
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
        
        if not cls.ELECTRICITY_MAPS_TOKEN:
            raise ValueError(
                "Missing Electricity Maps API token. Sign up at "
                "https://api-portal.electricitymaps.com and add token to .env file"
            )

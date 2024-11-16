"""
Main entry point for the French Grid Bluesky Bot.
"""
import pandas as pd
import os
from os import getcwd
import logging
from typing import Dict, Any
from energy_data.matchup import get_matchup
from energy_data.data_fetcher import get_data
from social.bluesky_client import send_bluesky_post
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnergyComparison:
    """
    A class to handle energy comparison data collection and posting to Bluesky.
    """
    def __init__(self, division: str):
        self.division = division
        self.zones = None
        self.data = None
        self.payload = None

    def get_matchup(self) -> None:
        """Fetch matchup data for the division."""
        try:
            self.zones = get_matchup(self.division)
            logger.info(f"Successfully fetched matchup for division {self.division}")
        except Exception as e:
            logger.error(f"Error getting matchup: {str(e)}")
            raise

    def get_data(self) -> None:
        """Fetch energy data for the zones."""
        if not self.zones:
            raise ValueError("Zones not set. Call get_matchup first.")
        try:
            self.data = get_data(self.zones)
            logger.info("Successfully fetched energy data")
        except Exception as e:
            logger.error(f"Error getting data: {str(e)}")
            raise

    def send_post(self) -> None:
        """Send post to Bluesky with the comparison data."""
        if not self.data:
            raise ValueError("Data not set. Call get_data first.")
        try:
            self.payload = send_bluesky_post(self.data)
            logger.info("Successfully posted to Bluesky")
        except Exception as e:
            logger.error(f"Error sending Bluesky post: {str(e)}")
            raise

def main() -> None:
    """Main function to run the energy comparison bot."""
    try:
        # Validate configuration
        Config.validate()
        
        wdb = getcwd()
        df = pd.read_csv(f"{wdb}/src/data/zones.csv")
        divisions = pd.unique(df['division'])
        
        for division in divisions:
            logger.info(f"Processing division: {division}")
            comparison = EnergyComparison(division)
            
            # Execute the comparison workflow
            comparison.get_matchup()
            comparison.get_data()
            comparison.send_post()
                
            logger.info(f"Successfully completed processing for division: {division}")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()

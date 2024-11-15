"""
Main entry point for the French Grid Bluesky Bot.
"""
import pandas as pd
import os
from os import getcwd
import requests
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
        if not Config.API_IP or not Config.API_PORT:
            raise ValueError("API_IP and API_PORT must be set in .env file")
        self.url = f"http://{Config.API_IP}:{Config.API_PORT}"
        self.latest_endpoint = "/getlatestmatchup"
        self.post_endpoint = "/entry"
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

    def save_entry(self) -> None:
        """Save the entry to the API if SAVE_POSTS is enabled."""
        if not self.payload:
            raise ValueError("Payload not set. Call send_post first.")
        
        try:
            # Get latest matchup
            latest_matchup_url = self.url + self.latest_endpoint
            response = requests.get(url=latest_matchup_url)
            response.raise_for_status()
            latest_matchup = response.json().get('matchup', 0)

            # Post entries
            post_url = self.url + self.post_endpoint
            for country_index, data in self.payload.items():
                payload = {
                    "division": self.division,
                    "country": data.get('country'),
                    "ts": int(data.get('ts')),
                    "matchup": latest_matchup + 1,
                    "co2": int(data.get('co2')),
                    "way_1": data.get('way_1'),
                    "way_1_pc": int(data.get('way_1_pc')),
                    "way_2": data.get('way_2'),
                    "way_2_pc": data.get('way_2_pc'),
                    "way_3": data.get('way_3'),
                    "way_3_pc": data.get('way_3_pc'),
                    "post_uri": data.get('post_uri')
                }
                response = requests.post(
                    url=post_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
            logger.info("Successfully saved entries to API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error saving entry to API: {str(e)}")
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
            
            if Config.SAVE_POSTS:
                comparison.save_entry()
                
            logger.info(f"Successfully completed processing for division: {division}")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()

"""
Client for interacting with the Electricity Maps API.
"""
import requests
from typing import Dict, Any, Optional
from ..config import Config

class ElectricityMapsClient:
    """Client for making requests to the Electricity Maps API."""
    
    BASE_URL = "https://api.electricitymap.org/v3"
    
    def __init__(self):
        """Initialize the client with API token from config."""
        if not Config.ELECTRICITY_MAPS_TOKEN:
            raise ValueError(
                "Electricity Maps API token not found. Sign up at "
                "https://api-portal.electricitymaps.com and add token to .env file"
            )
        self.headers = {'auth-token': Config.ELECTRICITY_MAPS_TOKEN}
    
    def check_health(self) -> bool:
        """
        Check if the Electricity Maps API is healthy.
        
        Returns:
            bool: True if API is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/health"
            )
            data = response.json()
            return (data.get('status') == 'ok' and 
                   data.get('monitors', {}).get('state') == 'ok')
        except Exception:
            return False
    
    def get_carbon_intensity(self, zone: str) -> Dict[str, Any]:
        """
        Get the latest carbon intensity for a zone.
        
        Args:
            zone: Zone identifier (e.g., 'FR' for France)
            
        Returns:
            Dictionary containing carbon intensity data
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = requests.get(
            f"{self.BASE_URL}/carbon-intensity/latest",
            params={'zone': zone},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_power_breakdown(self, zone: str) -> Dict[str, Any]:
        """
        Get the latest power breakdown for a zone.
        
        Args:
            zone: Zone identifier (e.g., 'FR' for France)
            
        Returns:
            Dictionary containing power breakdown data
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = requests.get(
            f"{self.BASE_URL}/power-breakdown/latest",
            params={'zone': zone},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_zone_data(self, zone: str) -> Dict[str, Any]:
        """
        Get both carbon intensity and power breakdown for a zone.
        
        Args:
            zone: Zone identifier (e.g., 'FR' for France)
            
        Returns:
            Dictionary containing combined zone data
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        carbon_data = self.get_carbon_intensity(zone)
        power_data = self.get_power_breakdown(zone)
        
        return {
            'zone': zone,
            'carbonIntensity': carbon_data.get('carbonIntensity'),
            'powerConsumption': power_data.get('powerConsumption'),
            'powerProduction': power_data.get('powerProduction'),
            'renewablePercentage': power_data.get('renewablePercentage'),
            'fossilFreePercentage': power_data.get('fossilFreePercentage')
        }

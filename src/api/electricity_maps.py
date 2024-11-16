import os
import logging
from typing import Dict, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

class ElectricityMapsAPI:
    BASE_URL = "https://api.electricitymap.org/v3"
    
    def __init__(self):
        self.token = os.getenv("ELECTRICITY_MAPS_TOKEN")
        if not self.token:
            raise ValueError("ELECTRICITY_MAPS_TOKEN environment variable not set")
        
        self.headers = {
            "auth-token": self.token
        }
    
    async def get_carbon_intensity(self, zone: str) -> Optional[Dict]:
        """Get the carbon intensity for a specific zone."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/carbon-intensity/latest",
                    params={"zone": zone},
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching carbon intensity for zone {zone}: {str(e)}")
            return None

    async def get_power_breakdown(self, zone: str) -> Optional[Dict]:
        """Get the power breakdown for a specific zone."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/power-breakdown/latest",
                    params={"zone": zone},
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching power breakdown for zone {zone}: {str(e)}")
            return None

    def get_top_sources(self, power_breakdown: Dict) -> list[tuple[str, float]]:
        """Extract top 3 power sources from power breakdown."""
        if not power_breakdown or 'powerConsumptionBreakdown' not in power_breakdown:
            return []
        
        consumption = power_breakdown['powerConsumptionBreakdown']
        total = power_breakdown.get('powerConsumptionTotal', 0)
        
        if total == 0:
            return []
        
        # Calculate percentages and sort
        sources = [
            (source, (value / total) * 100)
            for source, value in consumption.items()
            if value > 0 and source not in ['unknown', 'battery discharge', 'hydro discharge']
        ]
        
        return sorted(sources, key=lambda x: x[1], reverse=True)[:3]

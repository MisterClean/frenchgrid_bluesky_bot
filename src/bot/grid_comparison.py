import logging
import random
from typing import Dict, Optional, Tuple
import yaml
from datetime import datetime, timezone

from ..api.electricity_maps import ElectricityMapsAPI

logger = logging.getLogger(__name__)

class GridComparison:
    def __init__(self):
        self.api = ElectricityMapsAPI()
        self.countries = self._load_config()
        self.france_zone = "FR"

    def _load_config(self) -> list:
        """Load the list of countries from config file."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                return config.get("countries", [])
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            raise

    def _format_power_sources(self, sources: list[tuple[str, float]]) -> str:
        """Format the top power sources into a string."""
        return ", ".join(f"{source.replace('_', ' ')} {percentage:.0f}%" 
                        for source, percentage in sources)

    def _get_intensity_emoji(self, intensity: float) -> str:
        """Get an emoji based on carbon intensity."""
        if intensity < 100:
            return "🟢"  # Very low
        elif intensity < 200:
            return "🟡"  # Low
        elif intensity < 400:
            return "🟠"  # Medium
        else:
            return "🔴"  # High

    def _get_country_flag(self, country_code: str) -> str:
        """Convert country code to flag emoji."""
        # Convert country code to regional indicator symbols
        return "".join(chr(ord('🇦') + ord(c.upper()) - ord('A')) for c in country_code)

    async def get_comparison_data(self) -> Optional[str]:
        """Generate a comparison between France and a random country."""
        try:
            # Select random country
            comparison_country = random.choice(self.countries)
            
            # Get data for both countries
            fr_intensity = await self.api.get_carbon_intensity(self.france_zone)
            fr_power = await self.api.get_power_breakdown(self.france_zone)
            
            comp_intensity = await self.api.get_carbon_intensity(comparison_country)
            comp_power = await self.api.get_power_breakdown(comparison_country)
            
            if not all([fr_intensity, fr_power, comp_intensity, comp_power]):
                logger.error("Failed to fetch all required data")
                return None
            
            # Format the post
            fr_sources = self.api.get_top_sources(fr_power)
            comp_sources = self.api.get_top_sources(comp_power)
            
            fr_intensity_value = fr_intensity['carbonIntensity']
            comp_intensity_value = comp_intensity['carbonIntensity']
            
            # Get current UTC time
            current_time = datetime.now(timezone.utc).strftime("%H:%M UTC")
            
            post = (
                f"{self._get_country_flag('FR')} FRANCE: {fr_intensity_value:.0f}g CO2/kWh "
                f"{self._get_intensity_emoji(fr_intensity_value)} using {self._format_power_sources(fr_sources)}.\n\n"
                f"{self._get_country_flag(comparison_country)} {comparison_country}: {comp_intensity_value:.0f}g CO2/kWh "
                f"{self._get_intensity_emoji(comp_intensity_value)} using {self._format_power_sources(comp_sources)}.\n\n"
                f"Provided by @ElectricityMaps, data is about live consumption for the past hour as of {current_time}"
            )
            
            return post
            
        except Exception as e:
            logger.error(f"Error generating comparison: {str(e)}")
            return None

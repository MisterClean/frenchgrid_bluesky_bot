import logging
import random
from typing import Dict, Optional, Tuple
import yaml
from datetime import datetime, timedelta, timezone
import httpx

from api.electricity_maps import ElectricityMapsAPI

logger = logging.getLogger(__name__)

class GridComparison:
    def __init__(self):
        self.api = ElectricityMapsAPI()
        self.countries = self._load_config("countries")
        self.france_zone = "FR"
        self.emojis = self._load_config("emojis")
        self.account_tag = self._load_config("account_tag")
        self.power_source_emojis = self.emojis.get("power_sources", {})

    def _load_config(self, key: str) -> dict:
        """Load a specific key from the config file."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                return config.get(key, {})
        except Exception as e:
            logger.error(f"Failed to load config key '{key}': {str(e)}")
            raise

    def _get_intensity_emoji(self, intensity: float) -> str:
        """Get an emoji based on carbon intensity using config settings."""
        thresholds = self.emojis.get("thresholds", {})
        symbols = self.emojis.get("symbols", {})

        very_low_threshold = thresholds.get("very_low", 100)
        low_threshold = thresholds.get("low", 200)
        medium_threshold = thresholds.get("medium", 400)

        if intensity < very_low_threshold:
            return symbols.get("very_low", "🟢")
        elif intensity < low_threshold:
            return symbols.get("low", "🟡")
        elif intensity < medium_threshold:
            return symbols.get("medium", "🟠")
        else:
            return symbols.get("high", "🔴")

    def _get_country_flag(self, country_code: str) -> str:
        """Convert country code to flag emoji."""
        # Convert country code to regional indicator symbols
        return "".join(chr(ord('🇦') + ord(c.upper()) - ord('A')) for c in country_code)

    def _format_power_sources(self, power_breakdown: Dict) -> str:
        """Format the top 3 power sources with emojis from the configuration."""
        formatted_sources = []
        total_generation = sum(value for value in power_breakdown.values() if value > 0)

        if total_generation == 0:
            return "No power generation data available"

        # Calculate the percentage for each power source and sort by descending percentage
        sources_with_percentages = [
            (source, (value / total_generation) * 100)
            for source, value in power_breakdown.items()
            if value > 0 and source not in ['unknown', 'battery discharge', 'hydro discharge']
        ]

        # Sort by percentage in descending order and select the top 3 sources
        top_sources = sorted(sources_with_percentages, key=lambda x: x[1], reverse=True)[:3]

        for source, percentage in top_sources:
            emoji = self.power_source_emojis.get(source, "")
            formatted_sources.append(f"{emoji} {percentage:.0f}% {source.replace('_', ' ').capitalize()}")

        return "\n".join(formatted_sources)

    def _truncate_post(self, post: str, max_length: int = 300) -> str:
        """Truncate the post to ensure it fits within the maximum allowed length."""
        if len(post) <= max_length:
            return post
        return post[:max_length - 3] + "..."

    async def get_comparison_data(self) -> Optional[str]:
        """Generate a comparison between France and a random country."""
        try:
            # Determine the most recent complete hour
            now = datetime.now(timezone.utc)
            most_recent_complete_hour = now - timedelta(hours=1)
            formatted_timestamp = most_recent_complete_hour.strftime('%Y-%m-%dT%H:00:00Z')

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

            # Extract the timestamp from the API response (assuming 'datetime' field exists)
            fr_timestamp = fr_intensity.get('datetime')
            if not fr_timestamp:
                logger.error("No timestamp found in response data")
                return None

            # Convert the timestamp to a readable hour representation
            utc_time = datetime.strptime(fr_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M UTC")

            # Format the post
            fr_sources = self._format_power_sources(fr_power['powerConsumptionBreakdown'])
            comp_sources = self._format_power_sources(comp_power['powerConsumptionBreakdown'])

            fr_intensity_value = fr_intensity['carbonIntensity']
            comp_intensity_value = comp_intensity['carbonIntensity']

            post = (
                f"{self._get_country_flag('FR')} FRANCE: {fr_intensity_value:.0f}g CO2/kWh {self._get_intensity_emoji(fr_intensity_value)}\n"
                f"{fr_sources}\n\n"
                f"{self._get_country_flag(comparison_country)} {comparison_country}: {comp_intensity_value:.0f}g CO2/kWh {self._get_intensity_emoji(comp_intensity_value)}\n"
                f"{comp_sources}\n\n"
                f"{self.account_tag} ({utc_time})"
            )

            # Truncate post if needed to fit within 300 graphemes
            post = self._truncate_post(post)

            return post

        except Exception as e:
            logger.error(f"Error generating comparison: {str(e)}")
            return None

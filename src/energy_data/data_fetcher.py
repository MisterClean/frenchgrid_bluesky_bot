"""
Module for fetching and processing energy generation data from Electricity Maps API.
"""
from typing import List, Dict, Any
import logging
from .electricity_maps_client import ElectricityMapsClient

logger = logging.getLogger(__name__)

def calculate_top_sources(power_production: Dict[str, float]) -> List[tuple]:
    """
    Calculate the top 3 power sources and their percentages.
    
    Args:
        power_production: Dictionary of power sources and their values
        
    Returns:
        List of tuples containing (source, value, percentage)
    """
    # Filter out None values and zero production
    valid_sources = {
        source: value for source, value in power_production.items()
        if value is not None and value > 0
    }
    
    total = sum(valid_sources.values())
    if total == 0:
        return []
    
    # Calculate percentages and sort by production
    sources_with_pct = [
        (source, value, int((value / total) * 100))
        for source, value in valid_sources.items()
    ]
    
    return sorted(sources_with_pct, key=lambda x: x[1], reverse=True)[:3]

def get_data(zones: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch and process energy generation data for specified zones from Electricity Maps API.
    
    Args:
        zones: List of country/zone codes to fetch data for
        
    Returns:
        List of dictionaries containing processed energy data for each zone
        
    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    client = ElectricityMapsClient()
    
    # Check API health
    if not client.check_health():
        raise RuntimeError("Electricity Maps API is not healthy")
    
    result = []
    for zone in zones:
        try:
            # Get zone data
            data = client.get_zone_data(zone)
            
            # Get power production breakdown
            production = data.get('powerProduction', {})
            if not production:
                logger.warning(f"No power production data available for zone {zone}")
                continue
            
            # Calculate top 3 sources
            top3 = calculate_top_sources(production)
            if not top3:
                logger.warning(f"No valid power sources found for zone {zone}")
                continue
            
            # Get carbon intensity
            co2 = data.get('carbonIntensity')
            if co2 is None:
                logger.warning(f"No carbon intensity data available for zone {zone}")
                continue
            
            result.append({
                "country": zone,
                "co2": int(co2),
                "top3": top3,
                "renewable_pct": data.get('renewablePercentage', 0),
                "fossil_free_pct": data.get('fossilFreePercentage', 0)
            })
            
        except Exception as e:
            logger.error(f"Error fetching data for zone {zone}: {str(e)}")
            continue
    
    if not result:
        raise ValueError("No valid data could be fetched for any zone")
    
    return result

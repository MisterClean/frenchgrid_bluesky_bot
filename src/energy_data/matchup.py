"""
Module for determining country matchups for energy comparisons.
"""
import pandas as pd
import os
from typing import List
import random

def get_matchup(division: str) -> List[str]:
    """
    Get a random matchup of two countries from the specified division.
    
    Args:
        division: The division name to get countries from
        
    Returns:
        List containing two country codes for comparison
        
    Raises:
        ValueError: If division doesn't exist or has fewer than 2 countries
    """
    wdb = os.getcwd()
    zones_df = pd.read_csv(f"{wdb}/src/data/zones.csv")
    
    # Filter zones for the specified division
    division_zones = zones_df[zones_df['division'] == division]
    
    if division_zones.empty:
        raise ValueError(f"Division '{division}' not found in zones data")
        
    available_zones = division_zones['zone'].tolist()
    
    if len(available_zones) < 2:
        raise ValueError(f"Division '{division}' has fewer than 2 countries")
    
    # Randomly select two different zones
    selected_zones = random.sample(available_zones, 2)
    
    return selected_zones

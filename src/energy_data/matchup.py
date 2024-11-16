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
        List containing two zone IDs for comparison
        
    Raises:
        ValueError: If division doesn't exist or has fewer than 2 countries
    """
    wdb = os.getcwd()
    zones_df = pd.read_csv(f"{wdb}/src/data/zones.csv")
    
    # Clean column names to avoid issues with unexpected whitespace
    zones_df.columns = zones_df.columns.str.strip()
    
    # Filter zones for the specified division
    division_zones = zones_df[zones_df['division'] == division]
    
    if division_zones.empty:
        raise ValueError(f"Division '{division}' not found in zones data")
        
    # Ensure 'zone_id' column exists
    if 'zone_id' not in division_zones.columns:
        raise KeyError("The required 'zone_id' column is missing from zones.csv")
    
    available_zones = division_zones['zone_id'].tolist()
    
    if len(available_zones) < 2:
        raise ValueError(f"Division '{division}' has fewer than 2 countries")
    
    # Randomly select two different zone IDs
    selected_zones = random.sample(available_zones, 2)
    
    return selected_zones

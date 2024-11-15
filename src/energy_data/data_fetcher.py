"""
Module for fetching and processing energy generation data.
"""
import pandas as pd
import os
from typing import List, Dict, Any
from collections import defaultdict

def get_data(zones: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch and process energy generation data for specified zones.
    
    Args:
        zones: List of country/zone codes to fetch data for
        
    Returns:
        List of dictionaries containing processed energy data for each zone
    """
    # TODO: Implement actual API call to fetch real-time data
    # For now, using sample data for demonstration
    wdb = os.getcwd()
    probabilities = pd.read_csv(f"{wdb}/src/data/probabilities.csv")
    
    result = []
    for zone in zones:
        zone_data = probabilities[probabilities['zone'] == zone]
        if zone_data.empty:
            continue
            
        # Get top 3 generation methods
        top3 = []
        methods_data = defaultdict(float)
        
        for _, row in zone_data.iterrows():
            method = row['method']
            probability = row['probability']
            methods_data[method] += probability
            
        sorted_methods = sorted(
            methods_data.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for method, prob in sorted_methods[:3]:
            top3.append((method, prob, int(prob * 100)))
            
        # Calculate CO2 emissions (simplified example)
        co2 = sum(prob * 100 for _, prob, _ in top3) / 3
        
        result.append({
            "country": zone,
            "co2": int(co2),
            "top3": top3
        })
        
    return result

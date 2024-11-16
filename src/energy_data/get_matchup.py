from os import getcwd
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Load CSV files
wdb = getcwd()
zones_df = pd.read_csv(f"{wdb}/scripts/utils/zones.csv")
probabilities_df = pd.read_csv(f"{wdb}/scripts/utils/probabilities.csv")

# Clean column names
zones_df.columns = zones_df.columns.str.strip()
probabilities_df.columns = probabilities_df.columns.str.strip()

def get_matchup(division):
    """
    Get a random matchup of two countries from the specified division, weighted by probabilities.

    Args:
        division (str): The division to filter zones.

    Returns:
        pd.DataFrame: Zones of the two selected countries.

    Raises:
        ValueError: If the division has fewer than two countries.
    """
    logger.info(f"Fetching matchup for division: {division}")

    # Filter zones based on division
    zones_filtered = zones_df.loc[zones_df["division"] == division]
    if zones_filtered.empty:
        logger.error(f"No zones found for division '{division}'")
        raise ValueError(f"No zones found for division '{division}'")
    
    # Debugging: Log filtered zones
    logger.debug(f"Filtered zones for division '{division}':\n{zones_filtered}")

    # Merge probabilities
    zones_filtered = zones_filtered.merge(probabilities_df, on="country", how="left")
    if zones_filtered["p"].isnull().all():
        logger.error(f"No probabilities available for division '{division}'")
        raise ValueError(f"No probabilities available for division '{division}'")
    
    # Debugging: Log merged zones with probabilities
    logger.debug(f"Zones with probabilities for division '{division}':\n{zones_filtered}")

    # Get unique countries
    countries = pd.unique(zones_filtered["country"])
    if len(countries) < 2:
        logger.error(f"Division '{division}' has fewer than 2 countries")
        raise ValueError(f"Division '{division}' has fewer than 2 countries")

    # Filter probabilities for selected countries
    probabilities_filtered = probabilities_df[
        probabilities_df["country"].isin(countries)
    ]
    p = probabilities_filtered["p"].fillna(0).tolist()
    if sum(p) == 0:
        logger.warning("Probabilities sum to zero; using uniform distribution.")
        p = None

    # Randomly draw 2 countries
    try:
        choices = np.random.choice(countries, size=2, replace=False, p=p)
    except ValueError as e:
        logger.error(f"Error selecting countries: {str(e)}")
        raise ValueError("Could not select two countries for the matchup.")
    
    # Filter zones for the selected countries
    zones = zones_filtered[zones_filtered["country"].isin(choices)]

    # Debugging: Log the selected zones
    logger.debug(f"Selected zones:\n{zones}")

    return zones

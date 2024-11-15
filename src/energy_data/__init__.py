"""
Package for energy data collection and processing functionality.
"""
from .data_fetcher import get_data
from .matchup import get_matchup

__all__ = ['get_data', 'get_matchup']

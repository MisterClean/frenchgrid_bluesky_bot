"""
Bluesky social network client for posting energy comparison updates.
"""
import datetime
from collections import defaultdict
import pytz
from atproto import Client
from typing import Dict, List, Any
from ..config import Config

# Emoji mappings for countries and CO2 indicators
EMOJI_MAP = {
    "Sweden": "\U0001F1F8\U0001F1EA",
    "Portugal": "\U0001F1F5\U0001F1F9",
    "Germany": "\U0001F1E9\U0001F1EA",
    "Greece": "\U0001F1EC\U0001F1F7",
    "Norway": "\U0001F1F3\U0001F1F4",
    "Finland": "\U0001F1EB\U0001F1EE",
    "France": "\U0001F1EB\U0001F1F7",
    "UK": "\U0001F1EC\U0001F1E7",
    "Spain": "\U0001F1EA\U0001F1F8",
    "Italy": "\U0001F1EE\U0001F1F9",
    "Denmark": "\U0001F1E9\U0001F1F0",
    "Hungary": "\U0001F1ED\U0001F1FA",
    "Iceland": "\U0001F1EE\U0001F1F8",
    "Belgium": "\U0001F1E7\U0001F1EA",
    "Netherlands": "\U0001F1F3\U0001F1F1",
    "Ireland": "\U0001F1EE\U0001F1EA",
    "Poland": "\U0001F1F5\U0001F1F1",
    "co2_good": "\U0001F7E2",
    "co2_middle": "\U0001F7E0",
    "co2_bad": "\U0001F534",
}

def get_co2_emoji(co2_value: int) -> str:
    """
    Get the appropriate emoji for a CO2 value.
    
    Args:
        co2_value: CO2 emissions in g/kWh
        
    Returns:
        Emoji indicating CO2 level (green, orange, or red circle)
    """
    if 0 <= co2_value < 100:
        return EMOJI_MAP["co2_good"]
    elif 100 <= co2_value < 200:
        return EMOJI_MAP["co2_middle"]
    return EMOJI_MAP["co2_bad"]

def format_country_data(data: List[Dict[str, Any]]) -> Dict[str, List]:
    """
    Format country data for posting.
    
    Args:
        data: List of country data dictionaries
        
    Returns:
        Formatted data for post creation
    """
    data_post = defaultdict(list)
    for country in data:
        country_name = country["country"]
        data_post["country_name"].append(country_name)
        data_post["co2_emoji"].append(get_co2_emoji(country["co2"]))
        data_post["co2_number"].append(country["co2"])
        data_post["country_emoji"].append(EMOJI_MAP[country_name])
        data_post["top3"].append(country["top3"])
    return data_post

def create_post_text(data_post: Dict[str, List], timestamp_berlin: str) -> str:
    """
    Create the text content for the Bluesky post.
    
    Args:
        data_post: Formatted country data
        timestamp_berlin: Formatted timestamp string
        
    Returns:
        Formatted post text
    """
    return f"""{data_post['country_emoji'][0]} {data_post['country_name'][0].upper()}: {data_post['co2_number'][0]}g CO2/kWh {data_post['co2_emoji'][0]} \
using {data_post['top3'][0][0][2]}% {data_post['top3'][0][0][0].capitalize()}, \
{data_post['top3'][0][1][2]}% {data_post['top3'][0][1][0].capitalize()} \
and {data_post['top3'][0][2][2]}% {data_post['top3'][0][2][0].capitalize()}.

{data_post['country_emoji'][1]} {data_post['country_name'][1].upper()}: {data_post['co2_number'][1]}g CO2/kWh {data_post['co2_emoji'][1]} \
using {data_post['top3'][1][0][2]}% {data_post['top3'][1][0][0].capitalize()}, \
{data_post['top3'][1][1][2]}% {data_post['top3'][1][1][0].capitalize()} \
and {data_post['top3'][1][2][2]}% {data_post['top3'][1][2][0].capitalize()}.

Provided by @electricitymaps.bsky.social, data is about live consumption for the past hour as of {timestamp_berlin} Berlin's time.
"""

def send_bluesky_post(data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Send a post to Bluesky with energy comparison data.
    
    Args:
        data: List of country data dictionaries
        
    Returns:
        Dictionary containing formatted data for both countries with post URI
    """
    # Initialize Bluesky client
    client = Client()
    client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_PASSWORD)

    # Format data for posting
    data_post = format_country_data(data)
    
    # Get timestamp
    tz = pytz.timezone("Europe/Berlin")
    ts = datetime.datetime.now(tz)
    timestamp_berlin = ts.strftime("%d/%m/%y %H:%M")
    ts_unix = int(round(ts.timestamp()))
    
    # Create post text
    text = create_post_text(data_post, timestamp_berlin)
    
    # Send post
    response = client.send_post(text=text)
    post_uri = response.uri
    
    # Format response data
    result = {}
    for i, country_name in enumerate(['country_1', 'country_2']):
        result[country_name] = {
            "country": data_post["country_name"][i].upper(),
            "ts": ts_unix,
            "co2": data_post["co2_number"][i],
            "way_1": data_post["top3"][i][0][0].capitalize(),
            "way_1_pc": data_post["top3"][i][0][2],
            "way_2": data_post["top3"][i][1][0].capitalize(),
            "way_2_pc": data_post["top3"][i][1][2],
            "way_3": data_post["top3"][i][2][0].capitalize(),
            "way_3_pc": data_post["top3"][i][2][2],
            "post_uri": post_uri
        }
    
    return result

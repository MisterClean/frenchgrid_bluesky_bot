# French Grid Bluesky Bot

A Bluesky bot that posts regular updates comparing the carbon intensity of France's electrical grid with other European countries. The bot fetches data from ElectricityMaps API every 6 hours and creates posts showing:

- Carbon intensity (gCO2/kWh) for both countries
- Top 3 power sources and their percentages
- Visual indicators for carbon intensity levels
- Country flags

## Example Post

```
🇫🇷 FRANCE: 28g CO2/kWh 🟢 using 73% Nuclear, 12% Solar and 7% Hydro.

🇩🇪 GERMANY: 320g CO2/kWh 🔴 using 40% Wind, 20% Coal and 16% Solar.

Provided by @ElectricityMaps, data is about live consumption for the past hour as of 14:00 UTC
```

## Setup

1. Clone the repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   BLUESKY_HANDLE=your.handle.bsky.social
   BLUESKY_PASSWORD=your_password
   ELECTRICITY_MAPS_TOKEN=your_api_token
   SAVE_POSTS=false
   ```
5. Customize the list of countries to compare in `config.yaml`

## Configuration

The `config.yaml` file allows you to configure:

- List of European countries to compare with France
- Posting interval (in hours)
- Logging settings

## Running the Bot

```bash
python src/main.py
```

The bot will:
- Post updates at the configured interval (default: 6 hours)
- Log activities to bot.log
- Optionally save posts to posts.log if SAVE_POSTS=true

## Error Handling

The bot includes comprehensive error handling:
- Automatic retries for failed API requests
- Detailed logging of all activities and errors
- Graceful handling of API rate limits and network issues

## Logging

Logs are written to `bot.log` with configurable log levels and format. The logging configuration can be customized in `config.yaml`.

## License

MIT License

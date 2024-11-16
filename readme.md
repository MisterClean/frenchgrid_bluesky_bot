# French Grid Bluesky Bot

A Bluesky bot that compares electricity generation methods and CO2 emissions between European countries using real-time data from the Electricity Maps API.

## Features

- Posts regular updates about electricity generation methods and CO2 emissions
- Uses real-time data from Electricity Maps API
- Compares two countries at a time
- Shows top 3 electricity generation sources for each country
- Includes CO2 emissions data with visual indicators
- Displays renewable and fossil-free percentages

## Project Structure

```
frenchgrid_bluesky_bot/
├── .env.example           # Example environment variables
├── requirements.txt       # Project dependencies
├── src/                  # Source code
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── run.py           # Main entry point
│   ├── data/            # Data files
│   │   └── zones.csv    # Country division configurations
│   ├── energy_data/     # Energy data processing
│   │   ├── __init__.py
│   │   ├── electricity_maps_client.py  # Electricity Maps API client
│   │   ├── data_fetcher.py  # Energy data collection
│   │   └── matchup.py   # Country matchup selection
│   └── social/          # Social network integration
│       ├── __init__.py
│       └── bluesky_client.py  # Bluesky posting functionality
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/frenchgrid_bluesky_bot.git
cd frenchgrid_bluesky_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your credentials:
     ```ini
     # Bluesky credentials
     BLUESKY_HANDLE=your.handle.bsky.social
     BLUESKY_PASSWORD=your_password

     # Electricity Maps API
     ELECTRICITY_MAPS_TOKEN=your_api_token

     # Features
     SAVE_POSTS=false
     ```

### Electricity Maps API Access

To use this bot, you need an API token from Electricity Maps:

1. Sign up at [Electricity Maps API Portal](https://api-portal.electricitymaps.com)
2. Create an API token
3. Add the token to your `.env` file as `ELECTRICITY_MAPS_TOKEN`

The bot uses the following Electricity Maps API endpoints:
- `/v3/carbon-intensity/latest` - Get real-time carbon intensity data
- `/v3/power-breakdown/latest` - Get power generation breakdown
- `/v3/health` - Check API status

## Running the Bot

From the project root directory:
```bash
python -m src.run
```

## Development

The project follows Python best practices and conventions:

- Modular architecture with clear separation of concerns
- Type hints for better code clarity and IDE support
- Comprehensive error handling and logging
- Well-documented code with docstrings
- Clean package structure following Python conventions
- Environment-based configuration using .env files

### Key Components

- `src/config.py`: Configuration management using environment variables
- `src/energy_data/electricity_maps_client.py`: Client for Electricity Maps API
- `src/energy_data/data_fetcher.py`: Processes energy generation data
- `src/energy_data/matchup.py`: Handles country matchup selection
- `src/social/bluesky_client.py`: Handles Bluesky post creation and publishing

### Data Flow

1. The bot selects two countries to compare from the configured divisions
2. For each country, it fetches:
   - Real-time carbon intensity
   - Power generation breakdown
   - Renewable and fossil-free percentages
3. The data is processed to identify:
   - Top 3 power sources and their percentages
   - Current CO2 emissions
4. A formatted post is created and published to Bluesky

### Error Handling

The bot includes comprehensive error handling:
- API health checks before data fetching
- Validation of required configuration
- Graceful handling of missing or invalid data
- Detailed logging for troubleshooting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

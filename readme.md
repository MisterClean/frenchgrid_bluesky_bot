# French Grid Bluesky Bot

A Bluesky bot that compares electricity generation methods and CO2 emissions between European countries. Data is sourced from Electricity Maps.

## Features

- Posts regular updates about electricity generation methods and CO2 emissions
- Compares two countries at a time
- Shows top 3 electricity generation sources for each country
- Includes CO2 emissions data with visual indicators
- Saves historical data through an API (optional)

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
│   │   ├── zones.csv    # Country division configurations
│   │   └── probabilities.csv  # Energy generation probabilities
│   ├── energy_data/     # Energy data processing
│   │   ├── __init__.py
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

     # API configuration
     API_IP=api_ip_address
     API_PORT=api_port

     # Features
     SAVE_POSTS=false  # Set to true to enable saving posts to API
     ```

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
- `src/run.py`: Main entry point and orchestration
- `src/energy_data/`: Energy data collection and processing
  - `data_fetcher.py`: Fetches and processes energy generation data
  - `matchup.py`: Handles country matchup selection
- `src/social/`: Social network integration
  - `bluesky_client.py`: Handles Bluesky post creation and publishing

### Configuration

The bot uses environment variables for configuration, loaded from a `.env` file:

- `BLUESKY_HANDLE`: Your Bluesky handle (required)
- `BLUESKY_PASSWORD`: Your Bluesky password (required)
- `API_IP`: API server IP address (required if SAVE_POSTS=true)
- `API_PORT`: API server port (required if SAVE_POSTS=true)
- `SAVE_POSTS`: Enable/disable saving posts to API (optional, default: false)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

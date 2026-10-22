# French Grid Bluesky Bot

A Bluesky bot that posts regular updates comparing the carbon intensity of France's electrical grid with other European countries. The bot fetches data from ElectricityMaps API on a configurable schedule and creates posts showing:

- Carbon intensity (gCO2/kWh) for both countries
- Top 3 power sources and their percentages
- Visual indicators for carbon intensity levels
- Country flags
- Posting time in UTC
- Configurable emojis for different power sources

## Example Post

```
🇫🇷 FRANCE: 28g CO2/kWh 🟢
⚛️ 73% Nuclear
🌊 12% Hydro
🔥 7% Gas

🇩🇪 GERMANY: 320g CO2/kWh 🔴
💨 40% Wind
🪨 20% Coal
☀️ 16% Solar

Data [Electricity Maps](https://app.electricitymaps.com/) (14:00 UTC)
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
- Emojis for different power sources
- Thresholds for carbon intensity levels
- Account tag to be mentioned in posts

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


## Runtime security and deployment

Use Ubuntu's patched Python 3.12 and the hash-locked `requirements.txt`.
Regenerate it with `uv pip compile --python-version 3.12 --universal --upgrade --generate-hashes requirements.in -o requirements.txt`.
Run `python -m unittest discover -s tests -v` without production credentials.

The dedicated systemd service runs as `frenchgrid-bot`, with immutable releases
under `/opt/frenchgrid-bot/releases`, private credentials in
`/etc/frenchgrid-bot.env` (root-owned, mode 0600), and writable state/logs only
under `/var/lib/frenchgrid-bot`. The installer preserves the existing config.

For the initial migration, provision the environment file privately, stop the
legacy PM2 publisher, then extract the tested source release into `/opt/frenchgrid-bot/releases/<commit>`
and run `sudo bash deploy/install-service <commit> --activate` from that release.
Never run both supervisors simultaneously. Subsequent tested main commits publish immutable releases. A restricted host
timer polls their manifest, verifies the archive checksum, and runs the same
installer. CI needs no inbound SSH or production SSH private key. Enable
`frenchgrid-bot-update.timer` only after the initial PM2 migration is complete.

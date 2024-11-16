import os
import asyncio
import logging
import yaml
from datetime import datetime, timezone
from dotenv import load_dotenv
import signal

from bot.bluesky_bot import BlueskyBot
from bot.grid_comparison import GridComparison

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            logging_config = config.get("logging", {})

        log_level = getattr(logging, logging_config.get("level", "INFO").upper())
        log_format = logging_config.get("format", '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = logging_config.get("file", "bot.log")

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    except Exception as e:
        # Fallback logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("bot.log"),
                logging.StreamHandler()
            ]
        )
        logging.error(f"Failed to load logging config: {str(e)}")

logger = logging.getLogger(__name__)

class GridBot:
    def __init__(self):
        self.bluesky = BlueskyBot()
        self.grid = GridComparison()
        self.interval_hours = self._get_interval()

    def _get_interval(self) -> int:
        """Get posting interval from config."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                return config.get("post_interval_hours", 6)
        except Exception as e:
            logger.error(f"Failed to load interval from config: {str(e)}")
            return 6

    async def post_update(self):
        """Generate and post a grid comparison update."""
        try:
            post_content = await self.grid.get_comparison_data()
            if post_content:
                self.bluesky.create_post(post_content)
                logger.info("Successfully posted grid comparison update")
            else:
                logger.error("Failed to generate post content")
        except Exception as e:
            logger.error(f"Error posting update: {str(e)}")

    async def run(self):
        """Main bot loop."""
        logger.info(f"Starting bot with {self.interval_hours} hour interval")
        
        while True:
            try:
                await self.post_update()
                # Wait for the next interval
                await asyncio.sleep(self.interval_hours * 3600)
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                # Wait a bit before retrying
                await asyncio.sleep(300)

async def main():
    """Main entry point."""
    setup_logging()
    
    try:
        bot = GridBot()

        # Handle graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(bot)))

        await bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

async def shutdown(bot):
    """Graceful shutdown handler."""
    logger.info("Shutting down bot gracefully...")
    # Clean up if needed (e.g., close connections, save state)
    await asyncio.sleep(1)  # Simulate some cleanup delay
    logger.info("Bot shutdown complete")
    asyncio.get_event_loop().stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")

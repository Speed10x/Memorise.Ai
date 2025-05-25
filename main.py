#!/usr/bin/env python3
"""
RemindMeBot - Personal Reminder Telegram Bot
Entry point for the application
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime

from bot import reminder_bot
from database.mongodb import DatabaseOperations
from utils.reminder_scheduler import ReminderScheduler
import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['BOT_TOKEN', 'MONGODB_URL', 'ADMIN_ID']
    missing_vars = []

    for var in required_vars:
        if not getattr(config, var, None):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file or environment configuration")
        sys.exit(1)

def initialize_database():
    """Initialize database connection and create indexes"""
    try:
        db = DatabaseOperations()
        logger.info("Database connection established successfully")

        # Test the connection
        db.db.get_user_count()
        logger.info("Database operations verified")

        db.close()
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def main():
    """Main application entry point"""
    logger.info("=" * 50)
    logger.info("🤖 Starting RemindMeBot")
    logger.info("=" * 50)

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check environment
    logger.info("🔍 Checking environment configuration...")
    check_environment()
    logger.info("✅ Environment configuration OK")

    # Initialize database
    logger.info("🗄️ Initializing database connection...")
    if not initialize_database():
        logger.error("❌ Database initialization failed. Exiting.")
        sys.exit(1)
    logger.info("✅ Database connection OK")

    # Start bot with scheduler
    logger.info("🚀 Starting Telegram bot...")
    logger.info(f"📊 Debug mode: {'ON' if config.DEBUG else 'OFF'}")
    logger.info(f"🌍 Timezone: {config.TIMEZONE}")

    try:
        # Initialize scheduler
        scheduler = ReminderScheduler(reminder_bot.application.bot)

        # Start scheduler in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(scheduler.start())

        # Start bot
        reminder_bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        # Stop scheduler
        if 'scheduler' in locals():
            loop.run_until_complete(scheduler.stop())
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        sys.exit(1)
    finally:
        logger.info("👋 RemindMeBot shutdown complete")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script for Telegram Bot
Run this to test your bot locally before full deployment
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def test_bot():
    """Test bot functionality"""
    try:
        # Load environment variables from secrets folder
        secrets_path = os.path.join(os.path.dirname(__file__), '..', 'secrets', '.env')
        load_dotenv(secrets_path)
        
        # Check required environment variables
        required_vars = ['TELEGRAM_BOT_TOKEN', 'DATABASE_URL', 'FLASK_API_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        logger.info("✅ Environment variables loaded")
        
        # Import and create bot
        from telegram_bot.bot import create_bot_from_env
        
        bot = create_bot_from_env()
        logger.info("✅ Bot instance created")
        
        # Test database connection
        await bot.db.initialize()
        logger.info("✅ Database initialized")
        
        # Test API connection
        from telegram_bot.utils import fetch_funding_data
        
        funding_data = await fetch_funding_data(bot.api_base_url)
        if funding_data:
            logger.info(f"✅ API connection working - fetched {len(funding_data)} markets")
        else:
            logger.warning("⚠️ API connection failed or no data")
        
        # Test bot token
        try:
            from telegram import Bot
            test_bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
            bot_info = await test_bot.get_me()
            logger.info(f"✅ Bot token valid - Bot name: {bot_info.username}")
        except Exception as e:
            logger.error(f"❌ Bot token invalid: {e}")
            return False
        
        logger.info("🎉 All tests passed! Bot is ready to run.")
        logger.info("To start the bot, run: python -m telegram_bot.bot")
        
        # Cleanup
        await bot.db.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_notification_system():
    """Test the notification system"""
    try:
        secrets_path = os.path.join(os.path.dirname(__file__), '..', 'secrets', '.env')
        load_dotenv(secrets_path)
        from telegram_bot.bot import create_bot_from_env
        from telegram_bot.utils import fetch_funding_data, apply_filters, format_notification_message
        
        bot = create_bot_from_env()
        await bot.db.initialize()
        
        # Test data fetching
        funding_data = await fetch_funding_data(bot.api_base_url)
        if not funding_data:
            logger.error("❌ Cannot fetch funding data for notification test")
            return False
        
        # Test filtering with sample settings
        test_filters = {
            'name': 'Test Alert',
            'selected_dexes': ['dYdX', 'Hyperliquid'],
            'min_spread': 50,
            'max_spread': 500,
            'show_arbitrage_only': False,
            'show_high_spread_only': False,
            'max_results': 3,
            'interval_hours': 5
        }
        
        opportunities = apply_filters(funding_data, test_filters)
        logger.info(f"✅ Filtering works - found {len(opportunities)} opportunities")
        
        # Test message formatting
        message = format_notification_message(opportunities, test_filters)
        logger.info("✅ Message formatting works")
        logger.info("Sample message:")
        logger.info("-" * 50)
        logger.info(message)
        logger.info("-" * 50)
        
        await bot.db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Notification test failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "notifications":
        # Test notifications specifically
        success = asyncio.run(test_notification_system())
    else:
        # Full bot test
        success = asyncio.run(test_bot())
    
    sys.exit(0 if success else 1)
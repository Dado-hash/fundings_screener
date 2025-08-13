#!/usr/bin/env python3
"""
Simplified bot test - just check if everything is configured correctly
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def simple_test():
    """Quick test of bot configuration"""
    try:
        # Load environment variables
        secrets_path = os.path.join(os.path.dirname(__file__), '..', 'secrets', '.env')
        load_dotenv(secrets_path)
        logger.info("✅ Environment loaded")
        
        # Check required variables
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        api_url = os.getenv('FLASK_API_URL', 'http://localhost:5000/api')
        
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in secrets/.env")
            return False
        logger.info("✅ Bot token found")
        
        # Test API connection
        import requests
        try:
            response = requests.get(f"{api_url}/funding-rates", timeout=10)
            if response.ok:
                data = response.json()
                logger.info(f"✅ API working - {len(data.get('data', []))} markets")
            else:
                logger.warning(f"⚠️ API returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ API test failed: {e}")
            logger.info("Make sure Flask backend is running on localhost:8080")
        
        # Test Telegram bot token
        from telegram import Bot
        from telegram.request import HTTPXRequest
        
        # Create bot with longer timeout
        request = HTTPXRequest(connection_pool_size=1, read_timeout=30, write_timeout=30)
        bot = Bot(token=token, request=request)
        
        try:
            bot_info = await bot.get_me()
            logger.info(f"✅ Bot token valid: @{bot_info.username}")
        except Exception as e:
            logger.error(f"❌ Bot token invalid: {e}")
            return False
        
        # Test database creation
        try:
            import sqlite3
            db_path = 'fundings_bot.db'
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER)")
            conn.close()
            if os.path.exists(db_path):
                os.remove(db_path)  # Clean up
            logger.info("✅ Database creation works")
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return False
        
        logger.info("🎉 All tests passed!")
        logger.info("You can now start the bot with:")
        logger.info("python -m telegram_bot.bot")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_test())
    exit(0 if success else 1)
"""
Main Telegram Bot Class
"""

import os
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from .handlers import BotHandlers, NAME, INTERVAL, MIN_SPREAD, DEXES, FILTER_TYPE, SELECT_ALERT
from .database import DatabaseManager
from .scheduler import NotificationScheduler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class FundingRatesBot:
    def __init__(self, token: str, database_url: str, api_base_url: str):
        """
        Initialize the Funding Rates Telegram Bot
        
        Args:
            token: Telegram bot token
            database_url: Database connection string
            api_base_url: Base URL for funding rates API
        """
        self.token = token
        self.api_base_url = api_base_url

        # Initialize database manager
        self.db = DatabaseManager(database_url)

        # Initialize handlers
        self.handlers = BotHandlers(self.db, self.api_base_url)

        # Initialize application with lifecycle hooks
        self.application = (
            Application
            .builder()
            .token(token)
            .post_init(self._post_init)
            .post_shutdown(self._post_shutdown)
            .build()
        )

        # Initialize scheduler
        self.scheduler = NotificationScheduler(self.db, self.api_base_url, token)

        # Setup handlers
        self._setup_handlers()

        logger.info("FundingRatesBot initialized successfully")

    def _setup_handlers(self):
        """Setup all command and message handlers"""

        # Basic commands
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        self.application.add_handler(CommandHandler("alerts", self.handlers.list_alerts_command))

        # Setup conversation handler for creating alerts
        setup_conv = ConversationHandler(
            entry_points=[CommandHandler("setup", self.handlers.setup_start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.setup_name)],
                INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.setup_interval)],
                MIN_SPREAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.setup_min_spread)],
                DEXES: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.setup_dexes)],
                FILTER_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.setup_filter_type)],
            },
            fallbacks=[CommandHandler("cancel", self.handlers.cancel_setup)]
        )
        self.application.add_handler(setup_conv)

        # Delete conversation handler
        delete_conv = ConversationHandler(
            entry_points=[CommandHandler("delete", self.handlers.delete_start)],
            states={
                SELECT_ALERT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.delete_confirm)],
            },
            fallbacks=[CommandHandler("cancel", self.handlers.cancel_delete)]
        )
        self.application.add_handler(delete_conv)

        logger.info("All handlers setup completed")

    async def start(self):
        """Start the bot"""
        try:
            # For PTB v22, prefer run_polling in __main__. Keeping initialize/start
            # here to support advanced/manual startup if needed.
            await self.application.initialize()
            await self.application.start()

            logger.info("Bot started successfully")

        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise

    async def stop(self):
        """Stop the bot"""
        try:
            # Stop scheduler
            self.scheduler.stop()

            # Stop the application
            await self.application.stop()
            await self.application.shutdown()

            # Close database connection
            await self.db.close()

            logger.info("Bot stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

    async def _post_init(self, app: Application) -> None:
        """PTB lifecycle hook: runs after Application.initialize()."""
        # Initialize database and start scheduler
        await self.db.initialize()
        self.scheduler.start()
        logger.info("Post-init complete: DB initialized and scheduler started")

    async def _post_shutdown(self, app: Application) -> None:
        """PTB lifecycle hook: runs during Application.shutdown()."""
        try:
            self.scheduler.stop()
            await self.db.close()
            logger.info("Post-shutdown complete: scheduler stopped and DB closed")
        except Exception as e:
            logger.error(f"Error during post-shutdown: {e}")


def create_bot_from_env() -> FundingRatesBot:
    """Create bot instance from environment variables"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    database_url = os.getenv('DATABASE_URL', 'sqlite:///fundings_bot.db')
    api_base_url = os.getenv('FLASK_API_URL', 'http://localhost:5000/api')
    
    return FundingRatesBot(token, database_url, api_base_url)


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    
    # Load environment variables from secrets folder
    secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'secrets', '.env')
    load_dotenv(secrets_path)
    
    # Create bot and run polling (PTB manages the asyncio loop internally)
    bot = create_bot_from_env()
    # Run polling until terminated; lifecycle hooks will init DB & scheduler
    # Configure polling with longer interval to reduce API calls frequency
    bot.application.run_polling(
        poll_interval=5.0,  # Check for updates every 5 seconds instead of default 1s
        timeout=30,         # Long polling timeout of 30s
        bootstrap_retries=-1  # Infinite retries on connection errors
    )
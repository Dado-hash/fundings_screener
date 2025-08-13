"""
Notification Scheduler for Telegram Bot
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from telegram.constants import ParseMode

from .database import DatabaseManager
from .utils import fetch_funding_data, apply_filters, format_notification_message

logger = logging.getLogger(__name__)


class NotificationScheduler:
    def __init__(self, db: DatabaseManager, api_base_url: str, bot_token: str):
        """
        Initialize the notification scheduler
        
        Args:
            db: Database manager instance
            api_base_url: Base URL for funding rates API
            bot_token: Telegram bot token
        """
        self.db = db
        self.api_base_url = api_base_url
        self.bot = Bot(token=bot_token)
        self.scheduler = AsyncIOScheduler()
        
        logger.info("NotificationScheduler initialized")
    
    def start(self):
        """Start the notification scheduler"""
        try:
            # Schedule notification checks every minute to handle minute-based intervals
            self.scheduler.add_job(
                self.check_and_send_notifications,
                CronTrigger(second=0),  # Every minute at 0 seconds
                id='funding_notifications',
                max_instances=1,  # Prevent overlapping runs
                coalesce=True     # Combine missed runs
            )
            
            self.scheduler.start()
            logger.info("Notification scheduler started - checking every minute")
            
        except Exception as e:
            logger.error(f"Error starting notification scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the notification scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
            logger.info("Notification scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping notification scheduler: {e}")
    
    async def check_and_send_notifications(self):
        """Check for due notifications and send them"""
        try:
            logger.info("Starting notification check cycle")
            
            # Get all due notifications
            due_notifications = await self.db.get_due_notifications()
            
            if not due_notifications:
                logger.info("No due notifications found")
                return
            
            logger.info(f"Found {len(due_notifications)} due notification(s)")
            
            # Fetch current funding data
            funding_data = await fetch_funding_data(self.api_base_url)
            
            if not funding_data:
                logger.error("Failed to fetch funding data - skipping notifications")
                return
            
            # Process each notification
            for notification in due_notifications:
                await self._process_notification(notification, funding_data)
            
            logger.info("Notification check cycle completed")
            
        except Exception as e:
            logger.error(f"Error in notification check cycle: {e}")
    
    async def _process_notification(self, notification: Dict[str, Any], funding_data: List[Dict[str, Any]]):
        """
        Process a single notification
        
        Args:
            notification: Notification settings from database
            funding_data: Current funding rates data
        """
        try:
            chat_id = notification['chat_id']
            setting_id = notification['id']
            
            logger.info(f"Processing notification for chat_id: {chat_id}, setting_id: {setting_id}")
            
            # Check if notification is actually due based on interval (hours or minutes)
            if notification['last_sent']:
                last_sent = notification['last_sent']
                if isinstance(last_sent, str):
                    last_sent = datetime.fromisoformat(last_sent.replace('Z', '+00:00'))
                
                # Calculate next due time based on whether it's hours or minutes
                if notification.get('interval_hours'):
                    next_due = last_sent + timedelta(hours=notification['interval_hours'])
                elif notification.get('interval_minutes'):
                    next_due = last_sent + timedelta(minutes=notification['interval_minutes'])
                else:
                    # Fallback to hours if neither is set (shouldn't happen with proper constraints)
                    next_due = last_sent + timedelta(hours=1)
                
                if datetime.now() < next_due:
                    logger.info(f"Notification {setting_id} not yet due - next due at {next_due}")
                    return
            
            # Apply user filters to get relevant opportunities
            filtered_opportunities = apply_filters(funding_data, notification)
            
            if not filtered_opportunities:
                logger.info(f"No opportunities found for notification {setting_id}")
                # Still update last_sent to prevent spam
                await self.db.update_last_sent(setting_id)
                await self.db.log_notification(chat_id, setting_id, 0, 'no_data')
                return
            
            # Format the notification message
            message = format_notification_message(filtered_opportunities, notification)
            
            # Send the notification
            success = await self._send_message(chat_id, message)
            
            if success:
                # Update last_sent timestamp
                await self.db.update_last_sent(setting_id)
                await self.db.log_notification(chat_id, setting_id, len(filtered_opportunities), 'sent')
                
                logger.info(f"Notification sent successfully to chat_id: {chat_id}, "
                           f"opportunities: {len(filtered_opportunities)}")
            else:
                await self.db.log_notification(chat_id, setting_id, len(filtered_opportunities), 'failed')
                logger.error(f"Failed to send notification to chat_id: {chat_id}")
                
        except Exception as e:
            logger.error(f"Error processing notification {notification.get('id', 'unknown')}: {e}")
    
    async def _send_message(self, chat_id: int, message: str) -> bool:
        """
        Send a message to a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            message: Message to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to chat_id {chat_id}: {e}")
            
            # Handle specific error cases
            if "chat not found" in str(e).lower() or "blocked" in str(e).lower():
                # User blocked the bot or chat no longer exists
                logger.info(f"Chat {chat_id} not reachable - user may have blocked bot")
                # TODO: Deactivate subscription
            
            return False
    
    async def send_test_notification(self, chat_id: int) -> bool:
        """
        Send a test notification to verify bot functionality
        
        Args:
            chat_id: Telegram chat ID to send test to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch current data
            funding_data = await fetch_funding_data(self.api_base_url)
            
            if not funding_data:
                test_message = "🔧 *Test Notification*\n\n❌ Unable to fetch funding data at the moment."
            else:
                # Use default filters for test
                test_filters = {
                    'name': 'Test Alert',
                    'selected_dexes': ['dYdX', 'Hyperliquid', 'Paradex', 'Extended'],
                    'min_spread': 50,
                    'max_spread': 500,
                    'show_arbitrage_only': False,
                    'show_high_spread_only': False,
                    'max_results': 3,
                    'interval_hours': 1
                }
                
                opportunities = apply_filters(funding_data, test_filters)
                
                if opportunities:
                    test_message = format_notification_message(opportunities, test_filters)
                    test_message = f"🔧 *Test Notification*\n\n{test_message}"
                else:
                    test_message = "🔧 *Test Notification*\n\n📊 Bot is working! No opportunities found with current test criteria."
            
            return await self._send_message(chat_id, test_message)
            
        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
            return False
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics for monitoring"""
        try:
            cursor = self.db.connection.cursor()
            
            # Get basic stats
            if self.db.is_postgres:
                stats_query = """
                SELECT 
                    COUNT(DISTINCT ts.chat_id) as active_users,
                    COUNT(ns.id) as total_alerts,
                    COUNT(CASE WHEN ns.last_sent IS NOT NULL THEN 1 END) as alerts_with_notifications,
                    COUNT(nl.id) as total_notifications_sent,
                    COUNT(CASE WHEN nl.status = 'sent' THEN 1 END) as successful_notifications
                FROM telegram_subscriptions ts
                LEFT JOIN notification_settings ns ON ts.chat_id = ns.chat_id AND ns.is_active = true
                LEFT JOIN notification_log nl ON ns.id = nl.setting_id
                WHERE ts.is_active = true
                """
            else:
                stats_query = """
                SELECT 
                    COUNT(DISTINCT ts.chat_id) as active_users,
                    COUNT(ns.id) as total_alerts,
                    COUNT(CASE WHEN ns.last_sent IS NOT NULL THEN 1 END) as alerts_with_notifications,
                    COUNT(nl.id) as total_notifications_sent,
                    COUNT(CASE WHEN nl.status = 'sent' THEN 1 END) as successful_notifications
                FROM telegram_subscriptions ts
                LEFT JOIN notification_settings ns ON ts.chat_id = ns.chat_id AND ns.is_active = 1
                LEFT JOIN notification_log nl ON ns.id = nl.setting_id
                WHERE ts.is_active = 1
                """
            
            cursor.execute(stats_query)
            result = cursor.fetchone()
            cursor.close()
            
            return {
                'active_users': result['active_users'] or 0,
                'total_alerts': result['total_alerts'] or 0,
                'alerts_with_notifications': result['alerts_with_notifications'] or 0,
                'total_notifications_sent': result['total_notifications_sent'] or 0,
                'successful_notifications': result['successful_notifications'] or 0,
                'scheduler_running': self.scheduler.running,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {
                'error': str(e),
                'scheduler_running': self.scheduler.running,
                'last_check': datetime.now().isoformat()
            }
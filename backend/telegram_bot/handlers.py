"""
Telegram Bot Command Handlers
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from .database import DatabaseManager
from .utils import format_notification_message, apply_filters, fetch_funding_data

logger = logging.getLogger(__name__)

# Conversation states
NAME, INTERVAL, MIN_SPREAD, DEXES, FILTER_TYPE = range(5)
SELECT_ALERT = 10  # Use a different number to avoid conflict

AVAILABLE_DEXES = ['dYdX', 'Hyperliquid', 'Paradex', 'Extended']


class BotHandlers:
    def __init__(self, db: DatabaseManager, api_base_url: str):
        self.db = db
        self.api_base_url = api_base_url
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id if update.effective_user else None
        username = update.effective_user.username if update.effective_user else None
        
        # Create subscription
        await self.db.create_subscription(chat_id, user_id, username)
        
        welcome_message = """
🤖 *Welcome to Funding Rates Alert Bot!*

I'll help you track the best DeFi perpetual funding rate arbitrage opportunities and send you personalized notifications.

*Available Commands:*
/setup - Create a new custom alert
/alerts - View your active alerts
/delete - Delete an existing alert
/help - Show this help message

*How it works:*
1️⃣ Use `/setup` to create personalized alerts
2️⃣ Choose your preferred DEXes and filters
3️⃣ Set notification frequency (1-24 hours)
4️⃣ Receive automatic notifications with the best opportunities!

Ready to create your first alert? Use `/setup` to get started! 🚀
        """
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        
        logger.info(f"New user started bot: chat_id={chat_id}, username={username}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
🤖 *Funding Rates Alert Bot - Help*

*Commands:*
/start - Welcome message and bot introduction
/setup - Create a new notification alert
/alerts - List all your active alerts
/delete - Delete an existing alert
/help - Show this help message

*How to create alerts:*
1️⃣ Use `/setup` command
2️⃣ Follow the step-by-step configuration:
   • Alert name (for your reference)
   • Check interval (1-24 hours)  
   • Minimum spread threshold (in basis points)
   • Select DEXes to monitor
   • Choose filter type (all, arbitrage only, high spread only)

*Alert Types:*
🎯 *Arbitrage Opportunities* - Opposite funding rates (long/short)
📊 *High Spread* - Large differences between DEXes (≥100 bps)
📈 *All Opportunities* - Every market above your threshold

*Supported DEXes:*
• dYdX
• Hyperliquid  
• Paradex
• Extended

*Example Alert:*
"Bitcoin Arbitrage" - Every 5 hours, spread ≥150 bps, dYdX + Hyperliquid, arbitrage only

Questions? Just send me a message!
        """
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    # SETUP CONVERSATION HANDLERS
    async def setup_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the alert setup conversation"""
        setup_message = """
📝 *Let's create your custom alert!*

I'll guide you through a few simple questions to set up your personalized funding rate notifications.

*Step 1/5:* What would you like to name this alert?
Examples: "BTC Arbitrage", "High Spread ETH", "Daily Check"

Type your alert name:
        """
        
        await update.message.reply_text(setup_message, parse_mode=ParseMode.MARKDOWN)
        return NAME
    
    async def setup_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle alert name input"""
        name = update.message.text.strip()
        
        if len(name) > 50:
            await update.message.reply_text("⚠️ Alert name too long. Please use 50 characters or less:")
            return NAME
        
        context.user_data['alert_name'] = name
        
        interval_message = """
✅ Alert name set: "{}"

*Step 2/5:* How often should I check for opportunities?

Choose your notification frequency:

⚡ *High Frequency (minutes):*
• 5 = Every 5 minutes (very frequent, for active trading)
• 15 = Every 15 minutes (frequent updates)
• 30 = Every 30 minutes (regular monitoring)

⏰ *Standard Frequency (hours):*
• 1 = Every hour
• 5 = Every 5 hours (recommended)
• 12 = Twice a day
• 24 = Once a day

Enter either:
- A number with 'm' for minutes (e.g., "5m" for 5 minutes)
- A number with 'h' for hours (e.g., "5h" for 5 hours)
- Just a number (1-24 = hours, 5-60 = minutes)

Type your choice:
        """.format(name)
        
        await update.message.reply_text(interval_message, parse_mode=ParseMode.MARKDOWN)
        return INTERVAL
    
    async def setup_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle interval input"""
        try:
            text = update.message.text.strip().lower()
            
            # Check for minutes suffix
            if text.endswith('m') or text.endswith('min') or text.endswith('minutes'):
                # Extract number for minutes
                number_str = text.rstrip('minutes').rstrip('min').rstrip('m').strip()
                interval_minutes = int(number_str)
                
                if not 5 <= interval_minutes <= 60:
                    raise ValueError("Minutes must be between 5 and 60")
                
                context.user_data['interval_minutes'] = interval_minutes
                context.user_data['interval_hours'] = None
                frequency_text = f"Every {interval_minutes} minute{'s' if interval_minutes != 1 else ''}"
                
            elif text.endswith('h') or text.endswith('hour') or text.endswith('hours'):
                # Extract number for hours
                number_str = text.rstrip('hours').rstrip('hour').rstrip('h').strip()
                interval_hours = int(number_str)
                
                if not 1 <= interval_hours <= 24:
                    raise ValueError("Hours must be between 1 and 24")
                
                context.user_data['interval_hours'] = interval_hours
                context.user_data['interval_minutes'] = None
                frequency_text = f"Every {interval_hours} hour{'s' if interval_hours != 1 else ''}"
                
            else:
                # Default behavior: number alone
                interval = int(text)
                
                # If number is small (5-60), assume minutes; if larger (1-24), assume hours
                if 5 <= interval <= 60:
                    context.user_data['interval_minutes'] = interval
                    context.user_data['interval_hours'] = None
                    frequency_text = f"Every {interval} minute{'s' if interval != 1 else ''}"
                elif 1 <= interval <= 24:
                    context.user_data['interval_hours'] = interval
                    context.user_data['interval_minutes'] = None
                    frequency_text = f"Every {interval} hour{'s' if interval != 1 else ''}"
                else:
                    raise ValueError("Invalid interval")
                    
        except ValueError:
            await update.message.reply_text(
                "⚠️ Please enter a valid interval:\n"
                "• For minutes: 5-60 (e.g., '5m' or '15')\n"
                "• For hours: 1-24 (e.g., '5h' or '12')"
            )
            return INTERVAL
        
        spread_message = """
✅ Check interval set: {}

*Step 3/5:* What's your minimum spread threshold?

The spread is the difference between highest and lowest funding rates across DEXes.
Higher spreads = better arbitrage opportunities.

Enter minimum spread in basis points (bps):
• 50 = Small opportunities (0.5%)
• 100 = Medium opportunities (1%) - recommended
• 200 = Large opportunities (2%)
• 300+ = Rare, very large opportunities

Type a number (default is 100):
        """.format(frequency_text)
        
        await update.message.reply_text(spread_message, parse_mode=ParseMode.MARKDOWN)
        return MIN_SPREAD
    
    async def setup_min_spread(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle minimum spread input"""
        text = update.message.text.strip()
        
        if text.lower() in ['default', '']:
            min_spread = 100
        else:
            try:
                min_spread = float(text)
                if not 0 <= min_spread <= 1000:
                    raise ValueError()
            except ValueError:
                await update.message.reply_text("⚠️ Please enter a valid number between 0 and 1000, or 'default':")
                return MIN_SPREAD
        
        context.user_data['min_spread'] = min_spread
        
        dexes_message = """
✅ Minimum spread set: {} bps

*Step 4/5:* Which DEXes should I monitor?

Select the exchanges you want to include by typing their numbers separated by commas.

Available DEXes:
1️⃣ dYdX
2️⃣ Hyperliquid
3️⃣ Paradex  
4️⃣ Extended

*Examples:*
• "1,2" = dYdX + Hyperliquid
• "1,2,3,4" = All DEXes (recommended)
• "2,3" = Hyperliquid + Paradex

Type your selection (e.g. "1,2,4"):
        """.format(int(min_spread))
        
        await update.message.reply_text(dexes_message, parse_mode=ParseMode.MARKDOWN)
        return DEXES
    
    async def setup_dexes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle DEX selection"""
        try:
            selections = [int(x.strip()) for x in update.message.text.split(',')]
            if not all(1 <= s <= 4 for s in selections) or len(selections) < 2:
                raise ValueError()
        except ValueError:
            await update.message.reply_text(
                "⚠️ Please enter valid numbers separated by commas (e.g. '1,2,3'). "
                "You need at least 2 DEXes for meaningful spreads."
            )
            return DEXES
        
        selected_dexes = [AVAILABLE_DEXES[i-1] for i in selections]
        context.user_data['selected_dexes'] = selected_dexes
        
        dex_names = ", ".join(selected_dexes)
        filter_message = """
✅ DEXes selected: {}

*Step 5/5:* What type of opportunities do you want?

Choose your filter preference:

1️⃣ *All opportunities* - Every market above your spread threshold
2️⃣ *Best Arbitrage* - Only opposite funding rates (perfect for arbitrage trading)

Type 1 or 2:
        """.format(dex_names)
        
        await update.message.reply_text(filter_message, parse_mode=ParseMode.MARKDOWN)
        return FILTER_TYPE
    
    async def setup_filter_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle filter type selection and complete setup"""
        try:
            choice = int(update.message.text.strip())
            if choice not in [1, 2]:
                raise ValueError()
        except ValueError:
            await update.message.reply_text("⚠️ Please enter 1 or 2:")
            return FILTER_TYPE
        
        filter_names = {
            1: "All opportunities",
            2: "Best Arbitrage"
        }
        
        # Prepare setting data
        setting_data = {
            'chat_id': update.effective_chat.id,
            'name': context.user_data['alert_name'],
            'interval_hours': context.user_data.get('interval_hours'),
            'interval_minutes': context.user_data.get('interval_minutes'),
            'min_spread': context.user_data['min_spread'],
            'max_spread': 500,  # Default max
            'selected_dexes': context.user_data['selected_dexes'],
            'show_arbitrage_only': choice == 2,  # Only option 2 enables arbitrage filter
            'show_high_spread_only': False,      # Remove high spread filter
            'max_results': 5
        }
        
        # Save to database
        setting_id = await self.db.create_notification_setting(setting_data)
        
        if setting_id:
            # Create frequency text based on what was set
            if setting_data.get('interval_minutes'):
                frequency_text = f"Every {setting_data['interval_minutes']} minute{'s' if setting_data['interval_minutes'] != 1 else ''}"
                next_notification_time = setting_data['interval_minutes']
                next_notification_unit = "minute{'s' if setting_data['interval_minutes'] != 1 else ''}"
            else:
                frequency_text = f"Every {setting_data['interval_hours']} hour{'s' if setting_data['interval_hours'] != 1 else ''}"
                next_notification_time = setting_data['interval_hours']
                next_notification_unit = "hour{'s' if setting_data['interval_hours'] != 1 else ''}"
                
            summary_message = """
✅ *Alert Created Successfully!*

📋 *Alert Summary:*
🏷️ Name: {}
⏰ Frequency: {}
💰 Min Spread: {} bps
🔄 DEXes: {}
🎯 Filter: {}

Your first notification will be sent within {} {}.

Use /alerts to manage your alerts or /setup to create another one!
            """.format(
                setting_data['name'],
                frequency_text,
                int(setting_data['min_spread']),
                ", ".join(setting_data['selected_dexes']),
                filter_names[choice],
                next_notification_time,
                next_notification_unit
            )
            
            logger.info(f"Alert created: {setting_id} for chat_id: {update.effective_chat.id}")
        else:
            summary_message = "❌ Sorry, there was an error creating your alert. Please try again."
            logger.error(f"Failed to create alert for chat_id: {update.effective_chat.id}")
        
        await update.message.reply_text(summary_message, parse_mode=ParseMode.MARKDOWN)
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def cancel_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the setup conversation"""
        context.user_data.clear()
        await update.message.reply_text("❌ Alert setup cancelled. Use /setup to try again anytime!")
        return ConversationHandler.END
    
    # ALERTS MANAGEMENT
    async def list_alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        chat_id = update.effective_chat.id
        alerts = await self.db.get_user_alerts(chat_id)
        
        if not alerts:
            message = """
📝 *Your Alerts*

You don't have any active alerts yet.

Use /setup to create your first alert and start receiving notifications about the best funding rate opportunities!
            """
        else:
            message = "📝 *Your Active Alerts*\n\n"
            
            for i, alert in enumerate(alerts, 1):
                dex_list = ", ".join(alert['selected_dexes'])
                filter_type = "Arbitrage only" if alert['show_arbitrage_only'] else \
                             "High spread only" if alert['show_high_spread_only'] else \
                             "All opportunities"
                
                # Format interval text based on whether it's hours or minutes
                if alert.get('interval_minutes'):
                    interval_text = f"Every {alert['interval_minutes']} minute{'s' if alert['interval_minutes'] != 1 else ''}"
                else:
                    interval_text = f"Every {alert['interval_hours']} hour{'s' if alert['interval_hours'] != 1 else ''}"
                
                last_sent = "Never" if not alert['last_sent'] else \
                           datetime.fromisoformat(str(alert['last_sent'])).strftime("%m/%d %H:%M")
                
                message += f"""
{i}️⃣ *{alert['name']}*
⏰ {interval_text}
💰 Spread ≥ {int(alert['min_spread'])} bps
🔄 {dex_list}
🎯 {filter_type}
📤 Last sent: {last_sent}
🆔 ID: {alert['id']}

"""
            
            message += "Use /delete to remove an alert or /setup to create a new one."
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    # DELETE CONVERSATION
    async def delete_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the delete conversation"""
        chat_id = update.effective_chat.id
        alerts = await self.db.get_user_alerts(chat_id)
        
        if not alerts:
            await update.message.reply_text("You don't have any alerts to delete. Use /setup to create one!")
            return ConversationHandler.END
        
        message = "🗑️ *Select alert to delete:*\n\n"
        for i, alert in enumerate(alerts, 1):
            # Format interval text
            if alert.get('interval_minutes'):
                interval_text = f"Every {alert['interval_minutes']}m"
            else:
                interval_text = f"Every {alert['interval_hours']}h"
            
            message += f"{i}️⃣ {alert['name']} ({interval_text}) - ID: {alert['id']}\n"
        
        message += "\nType the alert ID number to delete it, or /cancel to abort:"
        
        context.user_data['alerts'] = alerts
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        return SELECT_ALERT
    
    async def delete_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle alert deletion"""
        try:
            alert_id = int(update.message.text.strip())
            alerts = context.user_data.get('alerts', [])
            
            # Find the alert
            alert_to_delete = None
            for alert in alerts:
                if alert['id'] == alert_id:
                    alert_to_delete = alert
                    break
            
            if not alert_to_delete:
                await update.message.reply_text("⚠️ Invalid alert ID. Please try again:")
                return SELECT_ALERT
            
        except ValueError:
            await update.message.reply_text("⚠️ Please enter a valid alert ID number:")
            return SELECT_ALERT
        
        # Delete the alert
        success = await self.db.delete_alert(update.effective_chat.id, alert_id)
        
        if success:
            message = f"✅ Alert '{alert_to_delete['name']}' has been deleted successfully!"
            logger.info(f"Alert {alert_id} deleted by chat_id: {update.effective_chat.id}")
        else:
            message = "❌ Error deleting alert. Please try again."
        
        await update.message.reply_text(message)
        context.user_data.clear()
        return ConversationHandler.END
    
    async def cancel_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the delete conversation"""
        context.user_data.clear()
        await update.message.reply_text("❌ Alert deletion cancelled.")
        return ConversationHandler.END
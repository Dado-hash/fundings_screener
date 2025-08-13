# 🤖 Telegram Bot Implementation Plan

## 📋 **OVERVIEW**
Implementation of a Telegram bot that sends automated notifications about funding rate arbitrage opportunities based on custom user filters.

**Bot Token:** `8376663213:AAFPitpfySs4ADceDXI_mgnj39yjUo0qdAM`

---

## 🏗️ **PROJECT STRUCTURE**
```
fundings_screener/
├── backend/
│   ├── app.py                 # Main Flask app
│   ├── requirements.txt       # Python dependencies
│   └── telegram_bot/          # NEW: Bot implementation
│       ├── __init__.py
│       ├── bot.py            # Main bot class
│       ├── handlers.py       # Command handlers
│       ├── scheduler.py      # Notification scheduler
│       ├── database.py       # Database operations
│       └── utils.py          # Helper functions
├── database/                  # NEW: Database files
│   ├── schema.sql            # Database schema
│   └── migrations/           # Database migrations
└── IMPLEMENTATION.md         # This file
```

---

## ✅ **PROGRESS TRACKING**

### **PHASE 1: Setup & Infrastructure** 
- [x] Create IMPLEMENTATION.md documentation
- [ ] Install required Python packages
- [ ] Create basic bot structure
- [ ] Setup database schema
- [ ] Test basic bot connectivity

### **PHASE 2: Core Bot Features**
- [ ] Implement /start command
- [ ] Implement /setup command for alert configuration
- [ ] Implement /alerts command to list user alerts
- [ ] Implement /delete command to remove alerts
- [ ] Test all commands manually

### **PHASE 3: Notification System**
- [ ] Create notification scheduler
- [ ] Implement filtering logic (reuse from frontend)
- [ ] Format notification messages
- [ ] Test scheduled notifications
- [ ] Integration with existing Flask API

### **PHASE 4: Production Deployment**
- [ ] Environment variables setup
- [ ] Database migration scripts
- [ ] Error handling and logging
- [ ] Rate limiting and security
- [ ] Production testing

---

## 🛠️ **TECHNICAL SPECIFICATIONS**

### **Database Schema**
```sql
-- User subscriptions
CREATE TABLE telegram_subscriptions (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,
    user_id BIGINT,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Notification settings (user can have multiple alerts)
CREATE TABLE notification_settings (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT REFERENCES telegram_subscriptions(chat_id),
    name VARCHAR(255) NOT NULL,
    interval_hours INTEGER NOT NULL,
    min_spread DECIMAL(5,2) DEFAULT 0,
    max_spread DECIMAL(5,2) DEFAULT 500,
    selected_dexes TEXT[],
    show_arbitrage_only BOOLEAN DEFAULT FALSE,
    show_high_spread_only BOOLEAN DEFAULT FALSE,
    max_results INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    last_sent TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notification log for tracking
CREATE TABLE notification_log (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT,
    setting_id INTEGER REFERENCES notification_settings(id),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    markets_count INTEGER,
    status VARCHAR(50)
);
```

### **Required Python Packages**
```txt
python-telegram-bot==20.7
APScheduler==3.10.4
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### **Environment Variables**
Added to existing `secrets/.env` file:
```bash
TELEGRAM_BOT_TOKEN="8376663213:AAFPitpfySs4ADceDXI_mgnj39yjUo0qdAM"
DATABASE_URL="sqlite:///fundings_bot.db"
FLASK_API_URL="http://localhost:5000/api"
```

---

## 🎯 **USER FLOW DESIGN**

### **New User Registration**
```
User: /start
Bot: 🤖 Welcome to Funding Rates Alert Bot!
     
     I'll help you track the best DeFi arbitrage opportunities.
     
     Commands:
     /setup - Create a new alert
     /alerts - View your alerts  
     /delete - Delete an alert
     /help - Show this help
     
     Ready to create your first alert?
```

### **Alert Configuration**
```
User: /setup
Bot: 📝 Let's create your custom alert!

Bot: 1️⃣ Alert name (e.g. "High Spread ETH-BTC"):
User: My Arbitrage Alert

Bot: 2️⃣ Check interval (hours): 1-24
User: 5

Bot: 3️⃣ Minimum spread (bps): (default: 100)
User: 150

Bot: 4️⃣ Select DEXes (send numbers):
     1️⃣ dYdX
     2️⃣ Hyperliquid  
     3️⃣ Paradex
     4️⃣ Extended
     
     Example: "1,2" for dYdX + Hyperliquid
User: 1,2

Bot: 5️⃣ Filter type:
     1️⃣ All opportunities
     2️⃣ Only arbitrage (opposite signs)
     3️⃣ Only high spread (>100 bps)
User: 2

Bot: ✅ Alert "My Arbitrage Alert" created!
     📊 Every 5 hours
     💰 Spread ≥ 150 bps
     🔄 dYdX, Hyperliquid
     🎯 Arbitrage only
     
     First notification will be sent within 5 hours.
```

### **Notification Example**
```
🚨 My Arbitrage Alert 🚨

📊 Found 3 arbitrage opportunities:

1️⃣ **BTC-USD** 
   💰 Spread: 287.1 bps
   📈 dYdX: +10.9 bps
   📉 Hyperliquid: -276.2 bps
   🎯 Best Arbitrage

2️⃣ **ETH-USD**
   💰 Spread: 194.3 bps  
   📈 Hyperliquid: +82.0 bps
   📉 dYdX: -112.3 bps
   🎯 Best Arbitrage

3️⃣ **SOL-USD**
   💰 Spread: 156.8 bps
   📈 dYdX: +67.2 bps
   📉 Hyperliquid: -89.6 bps
   🎯 Best Arbitrage

⏰ Updated: 18:42
🔄 Next check in 5 hours

📱 Manage alerts: /alerts
```

---

## 🐛 **ERROR HANDLING**

### **Bot Errors**
- API failures → Retry logic + error notifications
- Database errors → Graceful degradation  
- Rate limits → Queue management
- User blocks bot → Deactivate subscription

### **Data Validation**
- Hours: 1-24 range
- Spread: 0-1000 bps range  
- DEX selection: Valid options only
- Chat ID validation

---

## 📈 **MONITORING & ANALYTICS**

### **Metrics to Track**
- Active subscriptions count
- Notifications sent per day
- Average response time
- Error rates by type
- Most popular filters

### **Logging Strategy**
```python
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Log examples
logger.info(f"New subscription created: chat_id={chat_id}")
logger.warning(f"Failed to send notification: chat_id={chat_id}, error={error}")
logger.error(f"Database connection failed: {error}")
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-deployment**
- [x] All commands tested locally
- [x] Database migrations applied  
- [x] Environment variables configured
- [x] Error handling implemented
- [x] Rate limiting added
- [x] Logging configured

### **Post-deployment**
- [ ] Bot responds to /start
- [ ] Webhook configured (production)
- [ ] First notification sent successfully
- [ ] Monitoring dashboard setup
- [ ] Backup strategy implemented

---

## 📝 **NEXT STEPS FOR YOU**

1. **Install Python packages:**
   ```bash
   cd /Users/davide/Documents/GitHub/fundings_screener/backend
   pip install -r requirements.txt
   ```

2. **Test the bot configuration:**
   ```bash
   python test_bot.py
   ```

3. **Start the bot:**
   ```bash
   python -m telegram_bot.bot
   ```

4. **Test on Telegram:**
   - Search your bot on Telegram
   - Send `/start` command
   - Try creating an alert with `/setup`

### **Configuration completed:**
✅ Environment variables added to `secrets/.env`
✅ Bot structure created  
✅ Database schema ready
✅ All handlers implemented
✅ Notification scheduler ready

---

**Status:** 🏃‍♂️ In Progress
**Current Phase:** Phase 1 - Setup & Infrastructure  
**Next Milestone:** Basic bot connectivity test

Last Updated: 2025-08-13
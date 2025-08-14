#!/bin/bash

# 🚀 Script ottimizzato per avviare tutto con logs essenziali
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GRAY='\033[0;90m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Fundings Screener...${NC}"

# Create log directory
mkdir -p logs

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$FLASK_PID" ] && kill -0 $FLASK_PID 2>/dev/null; then
        kill $FLASK_PID
        echo -e "${GRAY}   • Flask API stopped${NC}"
    fi
    if [ ! -z "$BOT_PID" ] && kill -0 $BOT_PID 2>/dev/null; then
        kill $BOT_PID  
        echo -e "${GRAY}   • Telegram Bot stopped${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo -e "${GRAY}   • Frontend stopped${NC}"
    fi
    echo -e "${GREEN}✅ Clean shutdown completed${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Helper function to check service health
check_service() {
    local service=$1
    local url=$2
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service ready${NC}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service failed to start${NC}"
    return 1
}

# Start Flask API
echo -e "${YELLOW}🌐 Starting Flask API...${NC}"
cd backend
source venv/bin/activate
python3 app.py > ../logs/flask.log 2>&1 &
FLASK_PID=$!
cd ..

# Wait for Flask to be ready
if check_service "Flask API" "http://localhost:5001/api/health"; then
    echo -e "${GRAY}   • API running on port 5001${NC}"
    echo -e "${GRAY}   • Database initialized${NC}"
else
    echo -e "${RED}   • Check logs/flask.log for errors${NC}"
    exit 1
fi

# Start Telegram Bot
echo -e "${YELLOW}🤖 Starting Telegram Bot...${NC}"
cd backend
source venv/bin/activate
python3 -m telegram_bot.bot > ../logs/telegram.log 2>&1 &
BOT_PID=$!
cd ..
sleep 3

if kill -0 $BOT_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Telegram Bot ready${NC}"
    echo -e "${GRAY}   • Bot connected to Telegram${NC}"
    echo -e "${GRAY}   • Scheduler active${NC}"
else
    echo -e "${RED}❌ Telegram Bot failed${NC}"
    echo -e "${RED}   • Check logs/telegram.log for errors${NC}"
    exit 1
fi

# Start Frontend
echo -e "${YELLOW}🎨 Starting Frontend...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for Frontend to be ready  
if check_service "Frontend" "http://localhost:5173"; then
    echo -e "${GREEN}✅ Frontend ready${NC}"
    echo -e "${GRAY}   • React app compiled${NC}"
    echo -e "${GRAY}   • Admin dashboard available${NC}"
else
    echo -e "${RED}❌ Frontend failed${NC}"
    echo -e "${RED}   • Check logs/frontend.log for errors${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 ALL SERVICES RUNNING!${NC}"
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      📋 SERVICE STATUS                   ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║ 🌐 Flask API:      ${GREEN}http://localhost:5001${BLUE}             ║${NC}"
echo -e "${BLUE}║ 🤖 Telegram Bot:   ${GREEN}Connected & Active${BLUE}              ║${NC}"  
echo -e "${BLUE}║ 🎨 Frontend:       ${GREEN}http://localhost:5173${BLUE}             ║${NC}"
echo -e "${BLUE}║ 🔐 Admin Dashboard: ${GREEN}http://localhost:5173 → Admin${BLUE}    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"

echo ""
echo -e "${YELLOW}🔧 QUICK ACTIONS:${NC}"
echo -e "${GRAY}• Test bot:     Send /start to your Telegram bot${NC}"
echo -e "${GRAY}• Register:     /register command on Telegram${NC}"
echo -e "${GRAY}• Admin panel:  Open http://localhost:5173 → 'Admin'${NC}"
echo -e "${GRAY}• View logs:    tail -f logs/*.log${NC}"

echo ""
echo -e "${YELLOW}📊 MONITORING:${NC}"

# Enhanced monitoring with periodic status
monitor_count=0
while true; do
    sleep 10
    monitor_count=$((monitor_count + 1))
    
    # Check processes
    flask_ok=true
    bot_ok=true
    frontend_ok=true
    
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo -e "${RED}[$(date +'%H:%M:%S')] ❌ Flask API crashed${NC}"
        flask_ok=false
    fi
    
    if ! kill -0 $BOT_PID 2>/dev/null; then
        echo -e "${RED}[$(date +'%H:%M:%S')] ❌ Telegram Bot crashed${NC}"
        bot_ok=false
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}[$(date +'%H:%M:%S')] ❌ Frontend crashed${NC}"
        frontend_ok=false
    fi
    
    # Exit if any service crashed
    if [ "$flask_ok" = false ] || [ "$bot_ok" = false ] || [ "$frontend_ok" = false ]; then
        echo -e "${RED}💥 Service failure detected. Check logs/ directory${NC}"
        break
    fi
    
    # Show status every minute (6 cycles of 10s)
    if [ $((monitor_count % 6)) -eq 0 ]; then
        echo -e "${GRAY}[$(date +'%H:%M:%S')] 💚 All services healthy${NC}"
    fi
done

echo -e "${RED}🛑 Press Ctrl+C to stop all services${NC}"
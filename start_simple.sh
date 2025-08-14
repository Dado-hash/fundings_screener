#!/bin/bash

# 🚀 Script semplificato per avviare tutto (meno logs)
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Fundings Screener...${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${BLUE}Shutting down...${NC}"
    if [ ! -z "$FLASK_PID" ] && kill -0 $FLASK_PID 2>/dev/null; then
        kill $FLASK_PID
    fi
    if [ ! -z "$BOT_PID" ] && kill -0 $BOT_PID 2>/dev/null; then
        kill $BOT_PID
    fi
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start Flask API (suppress logs)
echo "🌐 Starting Flask API..."
cd backend
source venv/bin/activate
python3 app.py > /dev/null 2>&1 &
FLASK_PID=$!
cd ..
sleep 2

# Start Telegram Bot (suppress logs)
echo "🤖 Starting Telegram Bot..."
cd backend
source venv/bin/activate
python3 -m telegram_bot.bot > /dev/null 2>&1 &
BOT_PID=$!
cd ..
sleep 2

# Start Frontend (suppress logs)
echo "🎨 Starting Frontend..."
cd frontend
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 3

echo -e "${GREEN}✅ All services running!${NC}"
echo ""
echo "📋 Access URLs:"
echo "• Frontend:     http://localhost:5173"
echo "• Admin Panel:  http://localhost:5173 → Click 'Admin'"
echo "• API:          http://localhost:5001"
echo ""
echo "🔧 Check terminal for any errors."
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Monitor (silent)
while true; do
    sleep 5
    
    # Check if processes are still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "❌ Flask API crashed"
        break
    fi
    
    if ! kill -0 $BOT_PID 2>/dev/null; then
        echo "❌ Telegram Bot crashed"  
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend crashed"
        break
    fi
done
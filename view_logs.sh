#!/bin/bash

# 📝 Script per visualizzare i logs in tempo reale

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ ! -d "logs" ]; then
    echo -e "${RED}❌ No logs directory found. Start services first with ./start_simple.sh${NC}"
    exit 1
fi

echo -e "${BLUE}📝 Fundings Screener Logs Viewer${NC}"
echo ""

# Check which logs exist
echo -e "${YELLOW}Available logs:${NC}"
if [ -f "logs/flask.log" ]; then
    echo -e "${GREEN}• Flask API:      logs/flask.log${NC}"
fi
if [ -f "logs/telegram.log" ]; then
    echo -e "${GREEN}• Telegram Bot:   logs/telegram.log${NC}"
fi
if [ -f "logs/frontend.log" ]; then
    echo -e "${GREEN}• Frontend:       logs/frontend.log${NC}"
fi

echo ""
echo -e "${YELLOW}Select option:${NC}"
echo "1) View all logs (combined)"
echo "2) Flask API logs only"  
echo "3) Telegram Bot logs only"
echo "4) Frontend logs only"
echo "5) Last 50 lines of each log"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo -e "${BLUE}📊 Viewing all logs (press Ctrl+C to exit)${NC}"
        tail -f logs/*.log 2>/dev/null
        ;;
    2)
        if [ -f "logs/flask.log" ]; then
            echo -e "${BLUE}🌐 Flask API logs (press Ctrl+C to exit)${NC}"
            tail -f logs/flask.log
        else
            echo -e "${RED}❌ Flask log not found${NC}"
        fi
        ;;
    3)
        if [ -f "logs/telegram.log" ]; then
            echo -e "${BLUE}🤖 Telegram Bot logs (press Ctrl+C to exit)${NC}"
            tail -f logs/telegram.log
        else
            echo -e "${RED}❌ Telegram log not found${NC}"
        fi
        ;;
    4)
        if [ -f "logs/frontend.log" ]; then
            echo -e "${BLUE}🎨 Frontend logs (press Ctrl+C to exit)${NC}"
            tail -f logs/frontend.log
        else
            echo -e "${RED}❌ Frontend log not found${NC}"
        fi
        ;;
    5)
        echo -e "${BLUE}📋 Recent logs summary${NC}"
        echo ""
        if [ -f "logs/flask.log" ]; then
            echo -e "${GREEN}=== Flask API (last 10 lines) ===${NC}"
            tail -10 logs/flask.log
            echo ""
        fi
        if [ -f "logs/telegram.log" ]; then
            echo -e "${GREEN}=== Telegram Bot (last 10 lines) ===${NC}"
            tail -10 logs/telegram.log
            echo ""
        fi
        if [ -f "logs/frontend.log" ]; then
            echo -e "${GREEN}=== Frontend (last 10 lines) ===${NC}"
            tail -10 logs/frontend.log
        fi
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac
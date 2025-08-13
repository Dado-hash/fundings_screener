#!/bin/bash

# Environment Setup Script for Funding Rates Bot
# This script helps new contributors set up their environment quickly

echo "🚀 Setting up Funding Rates Bot environment..."

# Check if secrets/.env.template exists
if [ ! -f "secrets/.env.template" ]; then
    echo "❌ Error: secrets/.env.template not found!"
    echo "Make sure you're in the project root directory."
    exit 1
fi

# Check if secrets/.env already exists
if [ -f "secrets/.env" ]; then
    echo "⚠️  secrets/.env already exists."
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Your existing .env file is preserved."
        exit 0
    fi
fi

# Copy template to .env
echo "📋 Copying .env.template to .env..."
cp secrets/.env.template secrets/.env

echo "✅ Environment file created at secrets/.env"
echo ""
echo "🔧 Next steps:"
echo "1. Edit secrets/.env and replace placeholder values:"
echo "   - Get TELEGRAM_BOT_TOKEN from @BotFather on Telegram"
echo "   - Get RPC_URL from Infura (https://infura.io/)"
echo "   - Leave API keys empty if you don't have them"
echo ""
echo "2. Install dependencies:"
echo "   cd backend && pip install -r requirements.txt"
echo ""
echo "3. Test the bot:"
echo "   python backend/test_bot.py"
echo ""
echo "4. Start the bot:"
echo "   python -m backend.telegram_bot.bot"
echo ""
echo "📚 For detailed setup instructions, see:"
echo "   - secrets/README.md"
echo "   - IMPLEMENTATION.md"
echo ""
echo "🎉 Setup completed! Happy coding!"
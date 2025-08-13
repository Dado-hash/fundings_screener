# Secrets Configuration

⚠️ **SECURITY NOTICE**: Never commit actual API keys or secrets to version control!

## Setup Instructions

1. Copy the template file:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` and replace placeholder values with your actual API keys:
   ```bash
   # Replace YOUR_INFURA_PROJECT_ID with your actual Infura project ID
   RPC_URL=https://arbitrum-mainnet.infura.io/v3/YOUR_ACTUAL_PROJECT_ID
   ```

3. The `.env` file is automatically ignored by git and will never be committed.

## Required Environment Variables

### RPC_URL
- **Purpose**: Arbitrum blockchain RPC endpoint for smart contract interactions
- **Provider**: Infura (https://infura.io/)
- **Format**: `https://arbitrum-mainnet.infura.io/v3/{PROJECT_ID}`
- **How to get**: 
  1. Sign up at https://infura.io/
  2. Create a new project
  3. Copy the Project ID
  4. Use the Arbitrum mainnet endpoint

### TELEGRAM_BOT_TOKEN
- **Purpose**: Token for Telegram Bot API to send notifications
- **Provider**: Telegram (@BotFather)
- **Format**: `"1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`
- **How to get**:
  1. Open Telegram and search for @BotFather
  2. Send `/newbot` command
  3. Follow instructions to create your bot
  4. Copy the token provided

### DATABASE_URL
- **Purpose**: Database connection string for storing user alerts
- **Default**: `"sqlite:///fundings_bot.db"` (local SQLite file)
- **Production**: `"postgresql://user:pass@host:port/dbname"` (PostgreSQL)

### FLASK_API_URL
- **Purpose**: Base URL for the funding rates API
- **Default**: `"http://localhost:5000/api"`
- **Production**: Your deployed API URL

### API Keys (Optional)
- **DYDX_API_KEY**: For dYdX API access (leave empty for public endpoints)
- **HYPERLIQUID_API_KEY**: For Hyperliquid API access (leave empty for public endpoints)
- **PARADEX_API_KEY**: For Paradex API access (leave empty for public endpoints)

## Security Best Practices

- ✅ Use environment variables for all sensitive data
- ✅ Never hardcode API keys in source code
- ✅ Keep `.env` files local and never commit them
- ✅ Use different API keys for development and production
- ✅ Regularly rotate API keys
- ❌ Don't share API keys in chat/email/slack
- ❌ Don't commit `.env` files to version control
# Funding Rates Screener

A comprehensive web application for monitoring and analyzing cryptocurrency funding rates across multiple DEXs (Decentralized Exchanges) to identify arbitrage opportunities.

## 🎯 Features

- **Real-time data** from 4 major DEXs:
  - **dYdX**: Funding rates for perpetual markets
  - **Hyperliquid**: Predicted funding rates
  - **Paradex**: Funding rates for PERP markets
  - **Extended Exchange**: Funding rates for perpetual markets

- **Automatic spread analysis** to identify:
  - Arbitrage opportunities (spread > 100 bps)
  - High spreads (spread 50-100 bps)
  - Low spreads (spread < 50 bps)

- **Modern user interface** with:
  - Advanced filters for spreads and types
  - Aggregate statistics
  - Automatic updates every 3 minutes
  - Sortable table view
  - Automatic exclusion of markets with 0.0 bps spread

## 🏗️ Architecture

### Backend (Flask)
- **REST API** to serve funding rates data
- **Automatic background updates** every 3 minutes
- **Parallel fetching** from 4 DEXs to reduce latency
- **Robust error handling** for external APIs
- **Intelligent caching** with background thread for optimal performance
- **Flexible deployment**: Local (Flask) and cloud (Vercel)

### Frontend (React + TypeScript)
- **React 18** with Vite for fast builds
- **TypeScript** for type safety
- **TailwindCSS** for styling
- **Custom hooks** for state management
- **Reusable UI components** with shadcn/ui

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **npm** or **yarn**

### Installation and Setup

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd fundings_screener
   ```

2. **Configure environment variables**:
   ```bash
   # Copy the template and fill in your values
   cp secrets/.env.template secrets/.env
   
   # Edit secrets/.env with your API keys:
   # - TELEGRAM_BOT_TOKEN (get from @BotFather)
   # - RPC_URL (get from Infura)
   # - Other optional API keys
   ```
   
   📋 See `secrets/README.md` for detailed setup instructions.

3. **Start the application** (automatic script):
   ```bash
   ./start.sh
   ```

   This script:
   - Creates a Python virtual environment
   - Installs backend dependencies
   - Installs frontend dependencies
   - Starts backend (port 5000) and frontend (port 5173)

3. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000/api/funding-rates

### Manual Setup

If you prefer to start manually:

**Backend:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start server
cd backend
python app.py
```

**Frontend:**
```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

## 📊 Usage

### Data Interpretation

- **Rate**: Annualized funding rates in percentage
- **Spread**: Difference between the highest and lowest rate for the same asset
- **Opportunities**: 
  - 🔴 **Arbitrage** (spread > 100 bps): High potential opportunities
  - 🟡 **High Spread** (50-100 bps): Moderate opportunities  
  - 🟢 **Low Spread** (< 50 bps): Contained spreads

### Available Filters

- **Automatic filter**: Automatically excludes markets with 0.0 bps spread
- **Show only arbitrage opportunities**: Filters only assets with spread > 100 bps
- **Show high spreads**: Assets with spread between 50-100 bps
- **Show low spreads**: Assets with spread < 50 bps
- **Custom spread range**: Set min/max spread manually

### Update System

The application uses a **fully automatic system**:
- **Backend**: Background thread updates data every 3 minutes
- **Frontend**: Checks every 30 seconds for new available data
- **No manual controls**: Users cannot force updates
- **Zero wait**: Data is always available from cache

## 🔧 API Endpoints

### GET /api/funding-rates
Returns funding rates from all DEXs.

**Response:**
```json
{
  "data": [
    {
      "market": "ETH-USD",
      "dexRates": [
        {"dex": "dYdX", "rate": 45.2},
        {"dex": "Hyperliquid", "rate": 78.5},
        {"dex": "Paradex", "rate": -12.8}
      ],
      "volume24h": 0,
      "openInterest": 0,
      "lastUpdate": "2024-01-15T10:30:00Z"
    }
  ],
  "lastUpdate": "2024-01-15T10:30:00Z",
  "totalMarkets": 25
}
```

### GET /api/health
Backend health check.

## 🤖 Telegram Bot

**NEW**: Automated Telegram notifications for funding rate opportunities!

### Features
- 🔔 **Custom Alerts**: Set personalized notifications based on spread thresholds
- ⏰ **Flexible Intervals**: Choose notification frequency (1-24 hours)  
- 🎯 **Smart Filters**: Arbitrage-only, high-spread, or custom criteria
- 📱 **Easy Setup**: Step-by-step configuration via chat commands

### Bot Commands
- `/start` - Welcome and registration
- `/setup` - Create new alerts with custom filters
- `/alerts` - View your active alerts
- `/delete` - Remove existing alerts
- `/help` - Command reference

### Getting Started with Bot
1. **Create your bot**: Message @BotFather on Telegram, use `/newbot`
2. **Get the token**: Copy the token provided by @BotFather  
3. **Configure**: Add `TELEGRAM_BOT_TOKEN="your-token"` to `secrets/.env`
4. **Test**: Run `python backend/test_bot.py`
5. **Start**: Run `python -m backend.telegram_bot.bot`

📋 See `IMPLEMENTATION.md` for detailed bot setup instructions.

## 🔄 Technical Features

### Caching and Performance
- **Background threading**: Automatic updates every 3 minutes
- **Parallel fetching** from all 4 DEXs simultaneously
- **Frontend polling** every 30 seconds for new data
- **Intelligent cache**: Data always available, zero wait for users
- **Lazy loading** and React optimizations

### Error Handling
- Automatic retry on network errors
- Fallback to cached data on errors
- UI for error state management
- Detailed logging for debugging

### Security
- CORS configured for development environment
- Input validation on client and server side
- Timeout on external API calls
- Input data sanitization

## 🛠️ Development

### Project Structure
```
fundings_screener/
├── api/
│   └── funding-rates.py    # Vercel API function
├── backend/
│   ├── app.py              # Main Flask server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── pages/         # App pages
│   │   └── utils/         # Utility functions
│   └── package.json       # Node.js dependencies
├── test_*.py              # Testing scripts for each DEX
├── start.sh               # Automatic startup script
├── vercel.json            # Vercel deployment config
├── CLAUDE.md              # Detailed documentation for Claude
└── README.md
```

### Available Scripts

**Frontend:**
- `npm run dev`: Start dev server
- `npm run build`: Build for production
- `npm run preview`: Preview production build

**Backend:**
- `python app.py`: Start Flask server

## 📈 Roadmap

- [x] ✅ **Extended Exchange** integrated
- [x] ✅ **Automatic updates** every 3 minutes
- [x] ✅ **Vercel deployment** configured
- [x] ✅ **Automatic 0.0 spread filter**
- [ ] Add more DEXs (GMX, Gains Network, etc.)
- [ ] Implement WebSocket for real-time data
- [ ] Add historical charts
- [ ] Implement customizable alerts
- [ ] Add PnL calculation for strategies
- [ ] Real volume and open interest data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License. See the `LICENSE` file for details.
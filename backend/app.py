from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Cache per i dati dei funding rates
funding_cache = {}
last_update = None
CACHE_DURATION = 180  # 3 minuti
background_thread = None
app_initialized = False

def get_dydx_funding_rates():
    """Get funding rates from dYdX"""
    try:
        url = "https://indexer.dydx.trade/v4/perpetualMarkets"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        rates = {}
        for market, info in data["markets"].items():
            try:
                rate = float(info.get("nextFundingRate", 0))
                annualized_rate = rate * 24 * 365 * 100
                market_name = market.replace("-USD", "")
                rates[market_name] = annualized_rate
            except Exception:
                continue
        return rates
    except Exception as e:
        print(f"dYdX Error: {e}")
        return {}

def get_hyperliquid_funding_rates():
    """Get funding rates from Hyperliquid"""
    try:
        BASE_URL = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post(BASE_URL, json=payload, timeout=10)
        
        if response.ok:
            funding_data = response.json()
            coins = funding_data[0]['universe']
            data = funding_data[1]
            rates = {}
            
            for i, item in enumerate(coins):
                coin = item['name']
                rate = float(data[i]['funding']) * 24 * 365 * 100
                rates[coin] = rate
            return rates
        return {}
    except Exception as e:
        print(f"Hyperliquid Error: {e}")
        return {}

def get_paradex_funding_rates():
    """Get funding rates from Paradex"""
    try:
        BASE_URL = "https://api.prod.paradex.trade/v1"
        
        # Get all markets
        response = requests.get(f"{BASE_URL}/markets", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        markets = []
        for market in data['results']:
            if not market['asset_kind'] == 'PERP_OPTION':
                symbol = market['symbol']
                markets.append(symbol)
        
        # Get funding rates for each market
        rates = {}
        for market in markets:
            try:
                response = requests.get(f"{BASE_URL}/markets/summary", 
                                      params={"market": market}, timeout=5)
                response.raise_for_status()
                summary = response.json()
                funding_rate = summary["results"][0]["funding_rate"]
                annualized_rate = float(funding_rate) * 3 * 365 * 100
                market_name = market.replace("-USD-PERP", "")
                rates[market_name] = annualized_rate
            except Exception:
                continue
        
        return rates
    except Exception as e:
        print(f"Paradex Error: {e}")
        return {}

def get_extended_funding_rates():
    """Get funding rates from Extended Exchange"""
    try:
        EXTENDED_API = "https://api.extended.exchange/api/v1/"
        url = f"{EXTENDED_API}/info/markets"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        rates = {}
        for item in data['data']:
            try:
                symbol = item['name']
                # Remove -USD suffix
                symbol = symbol.replace("-USD", "")
                funding_rate = float(item['marketStats']['fundingRate'])
                annualized_rate = funding_rate * 24 * 365 * 100
                rates[symbol] = annualized_rate
            except Exception:
                continue
        
        return rates
    except Exception as e:
        print(f"Extended Error: {e}")
        return {}

def fetch_all_funding_rates():
    """Fetch funding rates from all DEXs"""
    print("Fetching funding rates...")
    
    # Fetch in parallelo usando threading
    results = {}
    threads = []
    
    def fetch_dydx():
        results['dydx'] = get_dydx_funding_rates()
    
    def fetch_hyperliquid():
        results['hyperliquid'] = get_hyperliquid_funding_rates()
    
    def fetch_paradex():
        results['paradex'] = get_paradex_funding_rates()
    
    def fetch_extended():
        results['extended'] = get_extended_funding_rates()
    
    threads.append(threading.Thread(target=fetch_dydx))
    threads.append(threading.Thread(target=fetch_hyperliquid))
    threads.append(threading.Thread(target=fetch_paradex))
    threads.append(threading.Thread(target=fetch_extended))
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return results

def update_funding_rates_background():
    """Aggiorna i funding rates in background ogni 3 minuti"""
    global funding_cache, last_update
    
    while True:
        try:
            print("Background update: Fetching new funding rates...")
            dex_data = fetch_all_funding_rates()
            funding_cache = combine_funding_data(dex_data)
            last_update = time.time()
            print(f"Background update: Updated data for {len(funding_cache)} markets")
        except Exception as e:
            print(f"Background update error: {e}")
        
        # Wait 3 minutes before next update
        time.sleep(CACHE_DURATION)

def start_background_updates():
    """Start background update thread"""
    global background_thread
    
    if background_thread is None or not background_thread.is_alive():
        background_thread = threading.Thread(target=update_funding_rates_background, daemon=True)
        background_thread.start()
        print("Background updates thread started")

def combine_funding_data(dex_data):
    """Combine data from all DEXs in uniform format"""
    combined_data = []
    
    # Get all unique markets
    all_markets = set()
    for dex_name, rates in dex_data.items():
        all_markets.update(rates.keys())
    
    for market in all_markets:
        dex_rates = []
        
        # dYdX
        if market in dex_data.get('dydx', {}):
            dex_rates.append({
                'dex': 'dYdX',
                'rate': round(dex_data['dydx'][market], 2)
            })
        
        # Hyperliquid
        if market in dex_data.get('hyperliquid', {}):
            dex_rates.append({
                'dex': 'Hyperliquid',
                'rate': round(dex_data['hyperliquid'][market], 2)
            })
        
        # Paradex
        if market in dex_data.get('paradex', {}):
            dex_rates.append({
                'dex': 'Paradex',
                'rate': round(dex_data['paradex'][market], 2)
            })
        
        # Extended
        if market in dex_data.get('extended', {}):
            dex_rates.append({
                'dex': 'Extended',
                'rate': round(dex_data['extended'][market], 2)
            })
        
        # Includi solo mercati con almeno 2 DEX
        if len(dex_rates) >= 2:
            combined_data.append({
                'market': f"{market}-USD",
                'dexRates': dex_rates,
                'volume24h': 0,  # Placeholder - potrebbe essere aggiunto in futuro
                'openInterest': 0,  # Placeholder
                'lastUpdate': datetime.now().isoformat()
            })
    
    return combined_data

@app.route('/api/funding-rates', methods=['GET'])
def get_funding_rates():
    """Endpoint per ottenere i funding rates"""
    global funding_cache, last_update, app_initialized
    
    # Al primo avvio, carica immediatamente i dati e avvia il background thread
    if not app_initialized:
        print("First startup: Loading initial data...")
        try:
            dex_data = fetch_all_funding_rates()
            funding_cache = combine_funding_data(dex_data)
            last_update = time.time()
            print(f"Initial data loaded for {len(funding_cache)} markets")
            
            # Start background updates
            start_background_updates()
            app_initialized = True
            
        except Exception as e:
            print(f"Initial loading error: {e}")
            return jsonify({'error': 'Unable to fetch funding rates'}), 500
    
    # If we don't have data yet (only possible in case of initial error)
    if not funding_cache:
        return jsonify({'error': 'No data available'}), 500
    
    return jsonify({
        'data': funding_cache,
        'lastUpdate': datetime.fromtimestamp(last_update).isoformat() if last_update else None,
        'totalMarkets': len(funding_cache)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_age': time.time() - last_update if last_update else None
    })

if __name__ == '__main__':
    print("Starting Funding Rates API server...")
    print("Endpoints:")
    print("  GET /api/funding-rates - Get funding rates from all DEXs")
    print("  GET /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
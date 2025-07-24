from http.server import BaseHTTPRequestHandler
import json
import requests
import threading
import time
from datetime import datetime

# Cache globale per i dati
_cache = {
    'data': [],
    'last_update': None
}
CACHE_DURATION = 180  # 3 minuti

def get_dydx_funding_rates():
    """Ottiene i funding rates da dYdX"""
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
        print(f"Errore dYdX: {e}")
        return {}

def get_hyperliquid_funding_rates():
    """Ottiene i funding rates da Hyperliquid"""
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
        print(f"Errore Hyperliquid: {e}")
        return {}

def get_paradex_funding_rates():
    """Ottiene i funding rates da Paradex"""
    try:
        BASE_URL = "https://api.prod.paradex.trade/v1"
        
        # Ottieni tutti i mercati
        response = requests.get(f"{BASE_URL}/markets", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        markets = []
        for market in data['results']:
            if not market['asset_kind'] == 'PERP_OPTION':
                symbol = market['symbol']
                markets.append(symbol)
        
        # Ottieni funding rates per ogni mercato
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
        print(f"Errore Paradex: {e}")
        return {}

def get_extended_funding_rates():
    """Ottiene i funding rates da Extended Exchange"""
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
                # Rimuovi il suffisso -USD
                symbol = symbol.replace("-USD", "")
                funding_rate = float(item['marketStats']['fundingRate'])
                annualized_rate = funding_rate * 24 * 365 * 100
                rates[symbol] = annualized_rate
            except Exception:
                continue
        
        return rates
    except Exception as e:
        print(f"Errore Extended: {e}")
        return {}

def fetch_all_funding_rates():
    """Fetch funding rates da tutti i DEX"""
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

def combine_funding_data(dex_data):
    """Combina i dati di tutti i DEX in un formato uniforme"""
    combined_data = []
    
    # Ottieni tutti i mercati unici
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
                'volume24h': 0,  # Placeholder
                'openInterest': 0,  # Placeholder
                'lastUpdate': datetime.now().isoformat()
            })
    
    return combined_data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _cache
        
        # Headers per CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Controlla se la cache è ancora valida
            current_time = time.time()
            if (_cache['last_update'] is None or 
                current_time - _cache['last_update'] > CACHE_DURATION or 
                not _cache['data']):
                
                print("Cache expired, fetching new data...")
                # Fetch nuovi dati
                dex_data = fetch_all_funding_rates()
                _cache['data'] = combine_funding_data(dex_data)
                _cache['last_update'] = current_time
                print(f"Fetched data for {len(_cache['data'])} markets")
            
            response_data = {
                'data': _cache['data'],
                'lastUpdate': datetime.fromtimestamp(_cache['last_update']).isoformat() if _cache['last_update'] else None,
                'totalMarkets': len(_cache['data'])
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            print(f"Errore: {e}")
            error_response = {'error': 'Unable to fetch funding rates'}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
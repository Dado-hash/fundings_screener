import requests
import pandas as pd

BASE_URL = "https://api.prod.paradex.trade/v1"

def get_all_markets():
    """Recupera tutti i mercati disponibili su Paradex"""
    try:
        response = requests.get(f"{BASE_URL}/markets")
        response.raise_for_status()
        data = response.json()
        markets = []
        for market in data['results']:
            if not market['asset_kind'] == 'PERP_OPTION':
                symbol = market['symbol']
                markets.append(symbol)
        return markets
    except Exception as e:
        print(f"Errore nel recupero dei mercati: {e}")
        return []

def get_funding_rates(markets):
    """Per ogni mercato, ottiene il funding rate attuale"""
    funding_rates = {}
    try:
        for market in markets:
            response = requests.get(f"{BASE_URL}/markets/summary", params={"market": market})
            response.raise_for_status()
            summary = response.json()
            funding_rate = summary["results"][0]["funding_rate"]
            funding_rates[market] = float(funding_rate) * 3 * 365 * 100
    except Exception as e:
        print(f"Errore nel recupero dei funding rate: {e}")
    return funding_rates

def main():
    print("🔄 Recupero lista mercati...")
    markets = get_all_markets()
    if not markets:
        print("❌ Nessun mercato trovato.")
        return

    print(f"📈 Trovati {len(markets)} mercati. Recupero funding rates...")
    funding_data = get_funding_rates(markets)

    print("\n📊 Funding Rates attuali:")
    for market, rate in funding_data.items():
        market = market.replace("-USD-PERP", "")
        print(f"{market}: {rate:.6f}" if rate is not None else f"{market}: N/D")

if __name__ == "__main__":
    main()
import requests

EXTENDED_API = "https://api.extended.exchange/api/v1/"
# If Extended requires authentication (e.g. HMAC), add the signing logic – adjust below as needed.

def get_funding_rate():
    url = f"{EXTENDED_API}/info/markets"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()  # expects { "symbol":..., "funding_rate":..., ... }

def main():
    funding_rates = get_funding_rate()
    
    rates = {}
    for item in funding_rates['data']:
        try:
            symbol = item['name']
            #rimuovi il suffisso -USD
            symbol = symbol.replace("-USD", "")
            rates[symbol] = float(item['marketStats']['fundingRate']) * 24 * 365 * 100
            print(f"{symbol}: {rates[symbol]}")
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    return rates

if __name__ == "__main__":
    funding_rates = main()
import requests
import json
from datetime import datetime

BASE_URL = "https://api.hyperliquid.xyz/info"

def get_predicted_funding_rates():
    payload = {
        "type": "metaAndAssetCtxs"
    }
    response = requests.post(BASE_URL, json=payload)
    if response.ok:
        #get the predicted funding rates for all perps and order them by descending order of funding rate
        funding_data = response.json()
        coins = funding_data[0]['universe']
        data = funding_data[1]
        funding_rates = []
        for i, item in enumerate(coins):
            coin = item['name']
            rate = float(data[i]['funding'])*24*365*100
            funding_rates.append((coin, rate))
        funding_rates.sort(key=lambda x: x[1], reverse=True)
        for coin, rate in funding_rates:
            print(f"{coin}: {rate:.4f}%")
    else:
        print("Failed to fetch predicted funding rates:", response.text)

if __name__ == "__main__":
    get_predicted_funding_rates()

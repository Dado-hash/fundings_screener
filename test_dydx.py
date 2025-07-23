import requests
import pandas as pd

def get_annualized_funding_rates():
    url = "https://indexer.dydx.trade/v4/perpetualMarkets"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    rows = []
    for market, info in data["markets"].items():
        try:
            rate = float(info.get("nextFundingRate", 0))
            annualized_rate = rate * 24 * 365 * 100
            rows.append({"market": market, "annualized_rate": annualized_rate})
        except Exception:
            continue  # salta mercati con dati mancanti o malformati

    df = pd.DataFrame(rows)
    df["market"] = df["market"].str.replace("-USD", "", regex=False)
    return df.sort_values(by="annualized_rate", ascending=False)

if __name__ == "__main__":
    dydx_rates = get_annualized_funding_rates()
    print(dydx_rates)

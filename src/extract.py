import requests

def fetch_market_data():
    url = "https://data-api.binance.vision/api/v3/klines"

    params = {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "limit": 5
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()  # Raise an exception for HTTP errors

    return url, params, response.json()
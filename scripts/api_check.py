import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from extract import fetch_market_data

url, params, data = fetch_market_data()

field_names = [
    "Open time", "Open price", "High price", "Low price", "Close price",
    "Volume", "Close time", "Quote asset volume", "Number of trades",
    "Taker buy base asset volume", "Taker buy quote asset volume", "Unused field",
]

for name, value in zip(field_names, data[0]):
    print(f"{name}: {value}")
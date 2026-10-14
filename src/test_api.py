from extract import fetch_market_data

data = fetch_market_data()

field_names = [
    "Open time",
    "Open price",
    "High price",
    "Low price",
    "Close price",
    "Volume",
    "Close time",
    "Quote asset volume",
    "Number of trades",
    "Taker buy base asset volume",
    "Taker buy quote asset volume",
    "Unused field"
]

first_candle = data[0]

for name, value in zip(field_names, first_candle):
    print(f"{name}: {value}")
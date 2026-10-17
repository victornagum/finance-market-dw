
import json
from config import get_connection
from datetime import datetime, timezone
from decimal import Decimal

query = """
    SELECT TOP 1
        ApiResponseID,
        ResponseJson
    FROM raw.ApiResponse
    ORDER BY ApiResponseID DESC;
"""

with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute(query)

    row = cursor.fetchone()

    if row is not None:
        api_response_id = row[0]
        data = json.loads(row[1])

field_names = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "number_of_trades",
    "taker_buy_base_volume",
    "taker_buy_quote_volume"
]

transformed_data = []

for candle in data:
    record = dict(zip(field_names, candle))

    record["open_time"] = datetime.fromtimestamp(
        record["open_time"] / 1000, tz=timezone.utc
    )

    record["close_time"] = datetime.fromtimestamp(
        record["close_time"] / 1000, tz=timezone.utc
    )

    for field in [
    "open", "high", "low", "close",
    "volume", "quote_volume",
    "taker_buy_base_volume",
    "taker_buy_quote_volume"
    ]:
        record[field] = Decimal(str(record[field]))
    transformed_data.append(record)

for record in transformed_data:
    if record["high"] < record["low"]:
        raise ValueError("Invalid candle: high is lower than low.")

    if record["high"] < max(record["open"], record["close"]):
        raise ValueError("Invalid candle: open or close exceeds high.")

    if record["low"] > min(record["open"], record["close"]):
        raise ValueError("Invalid candle: open or close is below low.")
    
    if record["volume"] < 0:
        raise ValueError("Invalid candle: volume cannot be negative.")
    
    if any(value is None for value in record.values()):
        raise ValueError("Invalid candle: missing value detected.")

    if len(data) != len(transformed_data):
        raise ValueError("Record count mismatch after transformation.")
    
print("Record count check passed!")
print("Data quality check passed!")
print("Transformation successful!")
print("Number of candles:", len(transformed_data))
print("First transformed candle:")
print(transformed_data[0])

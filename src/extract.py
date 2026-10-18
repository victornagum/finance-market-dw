import requests
from datetime import datetime, timezone

from config import get_connection


def fetch_market_data():
    url = "https://data-api.binance.vision/api/v3/klines"

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT MAX(OpenTime)
            FROM dw.FactMarketKline;
        """)

        latest_open_time = cursor.fetchone()[0]

    now = datetime.now(timezone.utc)

    # The current hour is still forming.
    # Use the previous hour's opening time as the latest closed candle.
    current_hour = now.replace(
        minute=0,
        second=0,
        microsecond=0
    )

    last_closed_open_time = current_hour.timestamp() * 1000 - 3600 * 1000

    params = {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "limit": 5 if latest_open_time is None else 1000,
    }

    if latest_open_time is not None:
        latest_timestamp_ms = int(
            latest_open_time.replace(
                tzinfo=timezone.utc
            ).timestamp() * 1000
        )

        params["startTime"] = latest_timestamp_ms - 3600 * 1000
        params["endTime"] = int(last_closed_open_time)

    response = requests.get(
        url,
        params=params,
        timeout=30
    )
    response.raise_for_status()

    return url, params, response.json()

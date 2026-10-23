
import requests
from datetime import datetime, timezone

from config import get_connection


def fetch_market_data(start_time_ms=None, end_time_ms=None, limit=None):
    url = "https://data-api.binance.vision/api/v3/klines"

    # Find the latest fully closed hourly candle.
    now = datetime.now(timezone.utc)
    current_hour = now.replace(
        minute=0,
        second=0,
        microsecond=0
    )
    last_closed_open_time_ms = int(
        current_hour.timestamp() * 1000 - 3600 * 1000
    )

    # Common API parameters.
    params = {
        "symbol": "BTCUSDT",
        "interval": "1h",
    }

    if start_time_ms is not None:
        # Historical extraction: use the requested date range.
        params["startTime"] = int(start_time_ms)

        requested_end = (
            last_closed_open_time_ms
            if end_time_ms is None
            else int(end_time_ms)
        )

        # Never request an unfinished hourly candle.
        params["endTime"] = min(
            requested_end,
            last_closed_open_time_ms
        )

        if params["startTime"] > params["endTime"]:
            raise ValueError(
                "Start time must not be later than the end time."
            )

        params["limit"] = 1000 if limit is None else int(limit)

    else:
        # Incremental extraction: continue from the warehouse.
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT MAX(OpenTime)
                FROM dw.FactMarketKline;
            """)
            latest_open_time = cursor.fetchone()[0]

        if latest_open_time is None:
            # Initial load: retrieve the latest five closed candles.
            params["limit"] = 5 if limit is None else int(limit)
        else:
            latest_timestamp_ms = int(
                latest_open_time.replace(
                    tzinfo=timezone.utc
                ).timestamp() * 1000
            )

            # Re-fetch the latest stored candle to catch updates,
            # then retrieve any newer closed candles.
            params["startTime"] = (
                latest_timestamp_ms - 3600 * 1000
            )
            params["endTime"] = last_closed_open_time_ms
            params["limit"] = 1000 if limit is None else int(limit)

    if not 1 <= params["limit"] <= 1000:
        raise ValueError("Limit must be between 1 and 1000.")

    response = requests.get(
        url,
        params=params,
        timeout=30
    )
    response.raise_for_status()

    return url, params, response.json()

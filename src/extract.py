import logging
from datetime import datetime, timezone

import requests

from config import db_connection

logger = logging.getLogger(__name__)

BINANCE_KLINES_URL = "https://data-api.binance.vision/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1h"
ONE_HOUR_MS = 60 * 60 * 1000


def last_closed_open_time_ms():
    """Open time (ms) of the latest fully closed hourly candle."""
    current_hour = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    )
    return int(current_hour.timestamp() * 1000) - ONE_HOUR_MS


def _latest_stored_open_time():
    with db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(OpenTime) FROM dw.FactMarketKline;")
        return cursor.fetchone()[0]


def fetch_market_data(start_time_ms=None, end_time_ms=None, limit=None):
    """Return (url, params, data). Only fully closed candles are requested."""
    last_closed_ms = last_closed_open_time_ms()

    params = {"symbol": SYMBOL, "interval": INTERVAL}

    if start_time_ms is not None:
        # Historical extraction: use the requested date range.
        requested_end = last_closed_ms if end_time_ms is None else int(end_time_ms)

        params["startTime"] = int(start_time_ms)
        # Never request an unfinished hourly candle.
        params["endTime"] = min(requested_end, last_closed_ms)

        if params["startTime"] > params["endTime"]:
            raise ValueError("Start time must not be later than the end time.")

        params["limit"] = 1000 if limit is None else int(limit)

    else:
        # Incremental extraction: continue from the warehouse.
        latest_open_time = _latest_stored_open_time()

        if latest_open_time is None:
            # Initial load: the latest five CLOSED candles.
            # FIX: endTime was missing, so Binance could return the
            # still-open current candle as the newest one.
            params["endTime"] = last_closed_ms
            params["limit"] = 5 if limit is None else int(limit)
        else:
            latest_ms = int(
                latest_open_time.replace(tzinfo=timezone.utc).timestamp() * 1000
            )
            # FIX: start AT the latest stored candle (re-fetch it to catch
            # corrections) -- the old "- 1 hour" started one candle earlier
            # than the comment said.
            params["startTime"] = latest_ms
            params["endTime"] = last_closed_ms
            params["limit"] = 1000 if limit is None else int(limit)

    if not 1 <= params["limit"] <= 1000:
        raise ValueError("Limit must be between 1 and 1000.")

    response = requests.get(BINANCE_KLINES_URL, params=params, timeout=30)
    response.raise_for_status()

    return BINANCE_KLINES_URL, params, response.json()

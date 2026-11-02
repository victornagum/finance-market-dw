import logging
from datetime import datetime, timezone

import requests

from config import db_connection

logger = logging.getLogger(__name__)

BINANCE_KLINES_URL = "https://data-api.binance.vision/api/v3/klines"
INTERVAL = "1h"
ONE_HOUR_MS = 60 * 60 * 1000
PAGE_SIZE = 1000


def last_closed_open_time_ms():
    """Return the open time of the latest fully closed hourly candle."""
    current_hour = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    )
    return int(current_hour.timestamp() * 1000) - ONE_HOUR_MS


def _latest_stored_open_time(pair_key):
    """Get the latest stored candle for one specific trading pair."""
    query = """
        SELECT MAX(OpenTime)
        FROM dw.FactMarketKline
        WHERE PairKey = ?;
    """

    with db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, pair_key)
        return cursor.fetchone()[0]


def fetch_market_data(
    symbol,
    pair_key,
    start_time_ms=None,
    end_time_ms=None,
    limit=None
):
    """Fetch Binance candles for a specific trading pair.

    Returns (url, params, data).
    Only fully closed candles are requested.
    """
    last_closed_ms = last_closed_open_time_ms()

    params = {
        "symbol": symbol,
        "interval": INTERVAL
    }

    if start_time_ms is not None:
        # Historical extraction.
        requested_end = (
            last_closed_ms
            if end_time_ms is None
            else int(end_time_ms)
        )

        params["startTime"] = int(start_time_ms)
        params["endTime"] = min(requested_end, last_closed_ms)
        params["limit"] = PAGE_SIZE if limit is None else int(limit)

        if params["startTime"] > params["endTime"]:
            raise ValueError(
                "Start time must not be later than the end time."
            )

    else:
        # Incremental extraction for this specific pair.
        latest_open_time = _latest_stored_open_time(pair_key)

        if latest_open_time is None:
            # Initial load: latest five fully closed candles.
            params["endTime"] = last_closed_ms
            params["limit"] = 5 if limit is None else int(limit)
        else:
            latest_ms = int(
                latest_open_time.replace(
                    tzinfo=timezone.utc
                ).timestamp() * 1000
            )

            # Re-fetch the latest stored candle to catch corrections.
            params["startTime"] = latest_ms
            params["endTime"] = last_closed_ms
            params["limit"] = PAGE_SIZE if limit is None else int(limit)

    if not 1 <= params["limit"] <= PAGE_SIZE:
        raise ValueError(
            f"Limit must be between 1 and {PAGE_SIZE}."
        )

    logger.info(
        "Requesting market data: symbol=%s, pair_key=%s",
        symbol,
        pair_key
    )

    response = requests.get(
        BINANCE_KLINES_URL,
        params=params,
        timeout=30
    )
    response.raise_for_status()

    return BINANCE_KLINES_URL, params, response.json()

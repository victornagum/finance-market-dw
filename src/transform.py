"""Pure transformation + validation logic (no DB access -> easy to unit test)."""
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

logger = logging.getLogger(__name__)

FIELD_NAMES = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "number_of_trades",
    "taker_buy_base_volume", "taker_buy_quote_volume",
]
DECIMAL_FIELDS = [
    "open", "high", "low", "close", "volume", "quote_volume",
    "taker_buy_base_volume", "taker_buy_quote_volume",
]
ONE_HOUR = timedelta(hours=1)
ONE_MS = timedelta(milliseconds=1)


def transform(data):
    """Convert raw Binance kline arrays into typed records."""
    records = []
    for candle in data:
        if len(candle) < len(FIELD_NAMES):
            raise ValueError(f"Malformed candle, too few fields: {candle!r}")

        # zip() drops Binance's 12th "unused" field automatically.
        record = dict(zip(FIELD_NAMES, candle))

        for field in ("open_time", "close_time"):
            record[field] = datetime.fromtimestamp(record[field] / 1000, tz=timezone.utc)

        for field in DECIMAL_FIELDS:
            record[field] = Decimal(str(record[field]))

        records.append(record)
    return records


def validate(records, expected_count=None):
    """Raise ValueError on bad data. Checks missing values FIRST."""
    if not records:
        raise ValueError("No candles to validate.")

    if expected_count is not None and len(records) != expected_count:
        raise ValueError("Record count mismatch after transformation.")

    seen_open_times = set()
    previous_open = None

    for record in records:
        # FIX: None check first, otherwise comparisons below raise TypeError.
        if any(value is None for value in record.values()):
            raise ValueError("Invalid candle: missing value detected.")

        if min(record["open"], record["high"], record["low"], record["close"]) <= 0:
            raise ValueError("Invalid candle: prices must be positive.")

        if record["high"] < record["low"]:
            raise ValueError("Invalid candle: high is lower than low.")
        if record["high"] < max(record["open"], record["close"]):
            raise ValueError("Invalid candle: open or close exceeds high.")
        if record["low"] > min(record["open"], record["close"]):
            raise ValueError("Invalid candle: open or close is below low.")

        if min(record["volume"], record["quote_volume"],
               record["taker_buy_base_volume"], record["taker_buy_quote_volume"]) < 0:
            raise ValueError("Invalid candle: volume cannot be negative.")
        if record["number_of_trades"] < 0:
            raise ValueError("Invalid candle: number of trades cannot be negative.")

        if record["close_time"] != record["open_time"] + ONE_HOUR - ONE_MS:
            raise ValueError(
                f"Invalid candle: close_time is not open_time + 1h - 1ms "
                f"({record['open_time']})."
            )

        if record["open_time"] in seen_open_times:
            raise ValueError(f"Duplicate candle at {record['open_time']}.")
        seen_open_times.add(record["open_time"])

        if previous_open is not None and record["open_time"] - previous_open != ONE_HOUR:
            logger.warning("Gap or disorder between %s and %s",
                           previous_open, record["open_time"])
        previous_open = record["open_time"]

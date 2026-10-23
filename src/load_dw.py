import logging

from config import db_connection
from read_raw import read_raw_response
from transform import transform, validate

logger = logging.getLogger(__name__)

SELECT_SQL = """
    SELECT OpenTime, CloseTime, OpenPrice, HighPrice, LowPrice, ClosePrice,
           Volume, QuoteVolume, NumberOfTrades,
           TakerBuyBaseVolume, TakerBuyQuoteVolume
    FROM dw.FactMarketKline
    WHERE OpenTime BETWEEN ? AND ?;
"""

INSERT_SQL = """
    INSERT INTO dw.FactMarketKline (
        OpenTime, CloseTime, OpenPrice, HighPrice, LowPrice, ClosePrice,
        Volume, QuoteVolume, NumberOfTrades,
        TakerBuyBaseVolume, TakerBuyQuoteVolume
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

UPDATE_SQL = """
    UPDATE dw.FactMarketKline
    SET CloseTime = ?, OpenPrice = ?, HighPrice = ?, LowPrice = ?, ClosePrice = ?,
        Volume = ?, QuoteVolume = ?, NumberOfTrades = ?,
        TakerBuyBaseVolume = ?, TakerBuyQuoteVolume = ?
    WHERE OpenTime = ?;
"""


def _values(record):
    """Non-key column values, in table order."""
    return (
        record["close_time"].replace(tzinfo=None),
        record["open"], record["high"], record["low"], record["close"],
        record["volume"], record["quote_volume"], record["number_of_trades"],
        record["taker_buy_base_volume"], record["taker_buy_quote_volume"],
    )


def load_to_dw(records):
    """Upsert records. Existing rows are fetched once, then we branch in Python."""
    open_times = [r["open_time"].replace(tzinfo=None) for r in records]
    inserted = updated = unchanged = 0

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(SELECT_SQL, min(open_times), max(open_times))
        existing = {row[0]: tuple(row[1:]) for row in cursor.fetchall()}

        for open_time, record in zip(open_times, records):
            new_values = _values(record)
            current = existing.get(open_time)

            if current is None:
                cursor.execute(INSERT_SQL, (open_time, *new_values))
                inserted += 1
            elif current == new_values:
                unchanged += 1
            else:
                cursor.execute(UPDATE_SQL, (*new_values, open_time))
                updated += 1

    # db_connection() commits here (or rolls everything back on error).
    return {"inserted": inserted, "updated": updated,
            "unchanged": unchanged, "processed": len(records)}


def load_dw(api_response_id=None):
    """Read a raw batch, transform, validate, and load it. Returns stats."""
    api_response_id, data = read_raw_response(api_response_id)

    records = transform(data)
    validate(records, expected_count=len(data))
    logger.info("Validation passed (ApiResponseID=%s, candles=%s).",
                api_response_id, len(records))

    stats = load_to_dw(records)
    logger.info("Warehouse load successful! inserted=%(inserted)s updated=%(updated)s "
                "unchanged=%(unchanged)s processed=%(processed)s", stats)
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    load_dw()

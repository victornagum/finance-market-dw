
import logging

from config import db_connection
from read_raw import read_raw_response
from transform import transform, validate

logger = logging.getLogger(__name__)


SELECT_SQL = """
    SELECT
        OpenTime,
        CloseTime,
        OpenPrice,
        HighPrice,
        LowPrice,
        ClosePrice,
        Volume,
        QuoteVolume,
        NumberOfTrades,
        TakerBuyBaseVolume,
        TakerBuyQuoteVolume
    FROM dw.FactMarketKline
    WHERE PairKey = ?
      AND OpenTime BETWEEN ? AND ?;
"""


INSERT_SQL = """
    INSERT INTO dw.FactMarketKline (
        PairKey,
        OpenTime,
        CloseTime,
        OpenPrice,
        HighPrice,
        LowPrice,
        ClosePrice,
        Volume,
        QuoteVolume,
        NumberOfTrades,
        TakerBuyBaseVolume,
        TakerBuyQuoteVolume
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""


UPDATE_SQL = """
    UPDATE dw.FactMarketKline
    SET
        CloseTime = ?,
        OpenPrice = ?,
        HighPrice = ?,
        LowPrice = ?,
        ClosePrice = ?,
        Volume = ?,
        QuoteVolume = ?,
        NumberOfTrades = ?,
        TakerBuyBaseVolume = ?,
        TakerBuyQuoteVolume = ?
    WHERE PairKey = ?
      AND OpenTime = ?;
"""


def _get_pair_key(symbol):
    """Retrieve the PairKey associated with a Binance symbol."""

    query = """
        SELECT PairKey
        FROM config.TradingPair
        WHERE Symbol = ?
          AND IsActive = 1;
    """

    with db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, symbol)
        row = cursor.fetchone()

    if row is None:
        raise LookupError(
            f"Active trading pair not found: {symbol}"
        )

    return row[0]


def _values(record):
    """Return non-key column values in table order."""

    return (
        record["close_time"].replace(tzinfo=None),
        record["open"],
        record["high"],
        record["low"],
        record["close"],
        record["volume"],
        record["quote_volume"],
        record["number_of_trades"],
        record["taker_buy_base_volume"],
        record["taker_buy_quote_volume"],
    )


def load_to_dw(records, pair_key):
    """Upsert records for one trading pair."""

    if not records:
        raise ValueError("No records to load.")

    open_times = [
        record["open_time"].replace(tzinfo=None)
        for record in records
    ]

    inserted = updated = unchanged = 0

    with db_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            SELECT_SQL,
            pair_key,
            min(open_times),
            max(open_times)
        )

        existing = {
            row[0]: tuple(row[1:])
            for row in cursor.fetchall()
        }

        for open_time, record in zip(open_times, records):
            new_values = _values(record)
            current = existing.get(open_time)

            if current is None:
                cursor.execute(
                    INSERT_SQL,
                    (pair_key, open_time, *new_values)
                )
                inserted += 1

            elif current == new_values:
                unchanged += 1

            else:
                cursor.execute(
                    UPDATE_SQL,
                    (*new_values, pair_key, open_time)
                )
                updated += 1

    return {
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "processed": len(records)
    }


def load_dw(api_response_id=None):
    """Read, transform, validate, and load one raw API response."""

    api_response_id, request_params, data = read_raw_response(
        api_response_id
    )

    symbol = request_params.get("symbol")

    if not symbol:
        raise ValueError(
            "Raw API response does not contain a symbol."
        )

    pair_key = _get_pair_key(symbol)

    records = transform(data)
    validate(records, expected_count=len(data))

    logger.info(
        "Validation passed: ApiResponseID=%s, symbol=%s, "
        "PairKey=%s, candles=%s",
        api_response_id,
        symbol,
        pair_key,
        len(records)
    )

    stats = load_to_dw(records, pair_key)

    
    logger.info(
        "Warehouse load successful: symbol=%s, "
        "inserted=%s updated=%s unchanged=%s processed=%s",
        symbol,
        stats["inserted"],
        stats["updated"],
        stats["unchanged"],
        stats["processed"]
    )

    return stats


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    load_dw()

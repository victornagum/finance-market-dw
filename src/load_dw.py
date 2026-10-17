
import runpy

from config import get_connection

# Run the existing extraction-from-raw,
# transformation, and validation script.
pipeline = runpy.run_path("src/read_raw.py")
transformed_data = pipeline["transformed_data"]

load_sql = """
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
    WHERE OpenTime = ?
      AND (
          CloseTime <> ?
          OR OpenPrice <> ?
          OR HighPrice <> ?
          OR LowPrice <> ?
          OR ClosePrice <> ?
          OR Volume <> ?
          OR QuoteVolume <> ?
          OR NumberOfTrades <> ?
          OR TakerBuyBaseVolume <> ?
          OR TakerBuyQuoteVolume <> ?
      );

    IF @@ROWCOUNT = 0
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM dw.FactMarketKline
            WHERE OpenTime = ?
        )
        BEGIN
            INSERT INTO dw.FactMarketKline (
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        END;
    END;
"""

values = [
    (
        record["open_time"].replace(tzinfo=None),
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
        record["open_time"].replace(tzinfo=None),
    )
    for record in transformed_data
]




with get_connection() as connection:
    cursor = connection.cursor()

    inserted_count = 0
    updated_count = 0
    unchanged_count = 0

    for record in transformed_data:
        open_time = record["open_time"].replace(tzinfo=None)
        close_time = record["close_time"].replace(tzinfo=None)

        new_values = (
            close_time,
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

        cursor.execute(
            """
            SELECT
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
            WHERE OpenTime = ?;
            """,
            open_time
        )

        existing = cursor.fetchone()

        if existing is None:
            inserted_count += 1
        elif tuple(existing) == new_values:
            unchanged_count += 1
        else:
            updated_count += 1

        parameters = (
            *new_values,
            open_time,
            *new_values,
            open_time,
            open_time,
            *new_values,
        )

        cursor.execute(load_sql, parameters)

    connection.commit()

    print("Warehouse load successful!")
    print("Rows inserted:", inserted_count)
    print("Rows updated:", updated_count)
    print("Rows unchanged:", unchanged_count)
    print("Rows processed:", len(transformed_data))

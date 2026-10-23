
import json
import subprocess
import sys
from datetime import datetime, timezone

from config import get_connection
from extract import fetch_market_data


ONE_HOUR_MS = 60 * 60 * 1000
THIRTY_DAYS_MS = 30 * 24 * ONE_HOUR_MS


def save_raw_response(endpoint, params, data):
    insert_sql = """
        INSERT INTO raw.ApiResponse (
            SourceName,
            Endpoint,
            RequestParams,
            ResponseJson
        )
        VALUES (?, ?, ?, ?);
    """

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            insert_sql,
            (
                "Binance",
                endpoint,
                json.dumps(params),
                json.dumps(data),
            ),
        )
        connection.commit()


def load_history():
    # Use complete hourly candles only.
    now = datetime.now(timezone.utc)
    current_hour = now.replace(
        minute=0,
        second=0,
        microsecond=0,
    )
    end_time_ms = int(
        current_hour.timestamp() * 1000 - ONE_HOUR_MS
    )

    # Start 30 days before the current hour.
    start_time_ms = end_time_ms - THIRTY_DAYS_MS + ONE_HOUR_MS

    total_batches = 0
    total_candles = 0

    while start_time_ms <= end_time_ms:
        endpoint, params, data = fetch_market_data(
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            limit=1000,
        )

        if not data:
            print("No more historical candles returned.")
            break

        # Save the API response before loading the warehouse.
        save_raw_response(endpoint, params, data)

        # Reuse the existing transformation, validation,
        # and warehouse upsert process.
        subprocess.run(
            [sys.executable, "src/load_dw.py"],
            check=True,
        )

        batch_count = len(data)
        total_batches += 1
        total_candles += batch_count

        print(f"Batch {total_batches} processed: {batch_count} candles.")

        # Advance one hour beyond the final candle received.
        last_open_time_ms = int(data[-1][0])
        next_start_time_ms = last_open_time_ms + ONE_HOUR_MS

        if next_start_time_ms <= start_time_ms:
            raise RuntimeError(
                "Historical pagination did not advance."
            )

        start_time_ms = next_start_time_ms

    print("\nHistorical load finished.")
    print("Batches processed:", total_batches)
    print("Candles fetched:", total_candles)


if __name__ == "__main__":
    load_history()

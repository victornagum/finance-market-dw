import logging

from extract import ONE_HOUR_MS, fetch_market_data, last_closed_open_time_ms
from load_dw import load_dw
from raw_store import save_raw_response

logger = logging.getLogger(__name__)


def load_history(days=30):
    end_time_ms = last_closed_open_time_ms()
    start_time_ms = end_time_ms - days * 24 * ONE_HOUR_MS + ONE_HOUR_MS

    total_batches = 0
    total_candles = 0

    while start_time_ms <= end_time_ms:
        endpoint, params, data = fetch_market_data(
            start_time_ms=start_time_ms, end_time_ms=end_time_ms, limit=1000
        )

        if not data:
            logger.info("No more historical candles returned.")
            break

        # Save raw first, then load THIS exact batch by ID
        # (no subprocess, no "latest row" guessing).
        api_response_id = save_raw_response(endpoint, params, data)
        load_dw(api_response_id)

        total_batches += 1
        total_candles += len(data)
        logger.info("Batch %s processed: %s candles.", total_batches, len(data))

        next_start_time_ms = int(data[-1][0]) + ONE_HOUR_MS
        if next_start_time_ms <= start_time_ms:
            raise RuntimeError("Historical pagination did not advance.")
        start_time_ms = next_start_time_ms

    logger.info("Historical load finished. Batches=%s Candles=%s",
                total_batches, total_candles)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    load_history()

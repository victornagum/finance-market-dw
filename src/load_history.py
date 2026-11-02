
import logging

from extract import ONE_HOUR_MS, fetch_market_data, last_closed_open_time_ms
from load_dw import load_dw
from raw_store import save_raw_response
from trading_pairs import get_active_trading_pairs

logger = logging.getLogger(__name__)

PAGE_SIZE = 1000


def _load_pair_history(pair, days):
    """Backfill historical candles for one trading pair."""

    pair_key = pair["pair_key"]
    symbol = pair["symbol"]

    end_time_ms = last_closed_open_time_ms()
    start_time_ms = (
        end_time_ms - days * 24 * ONE_HOUR_MS + ONE_HOUR_MS
    )

    total_batches = 0
    totals = {
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "processed": 0
    }

    logger.info(
        "[%s] Starting historical load: days=%s",
        symbol,
        days
    )

    while start_time_ms <= end_time_ms:
        endpoint, params, data = fetch_market_data(
            symbol=symbol,
            pair_key=pair_key,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            limit=PAGE_SIZE
        )

        if not data:
            logger.info("[%s] No more historical candles returned.", symbol)
            break

        # Save raw first, then load this exact batch.
        api_response_id = save_raw_response(
            endpoint,
            params,
            data
        )

        stats = load_dw(api_response_id)

        for key in totals:
            totals[key] += stats[key]

        total_batches += 1

        logger.info(
            "[%s] Batch %s processed: fetched=%s inserted=%s "
            "updated=%s unchanged=%s",
            symbol,
            total_batches,
            len(data),
            stats["inserted"],
            stats["updated"],
            stats["unchanged"]
        )

        # Continue from the next candle after the last returned candle.
        next_start_time_ms = int(data[-1][0]) + ONE_HOUR_MS

        if next_start_time_ms <= start_time_ms:
            raise RuntimeError(
                f"[{symbol}] Historical pagination did not advance."
            )

        start_time_ms = next_start_time_ms

    logger.info(
        "[%s] Historical load finished: batches=%s "
        "inserted=%s updated=%s unchanged=%s processed=%s",
        symbol,
        total_batches,
        totals["inserted"],
        totals["updated"],
        totals["unchanged"],
        totals["processed"]
    )

    return totals


def load_history(days=30):
    """Backfill historical candles for every active trading pair."""

    pairs = get_active_trading_pairs()

    if not pairs:
        raise RuntimeError("No active trading pairs found.")

    logger.info(
        "Starting multi-pair historical load: pairs=%s, days=%s",
        len(pairs),
        days
    )

    grand_totals = {
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "processed": 0
    }

    for pair in pairs:
        stats = _load_pair_history(pair, days)

        for key in grand_totals:
            grand_totals[key] += stats[key]

    logger.info(
        "Multi-pair historical load completed: "
        "inserted=%s updated=%s unchanged=%s processed=%s",
        grand_totals["inserted"],
        grand_totals["updated"],
        grand_totals["unchanged"],
        grand_totals["processed"]
    )

    return grand_totals


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    load_history(days=30)

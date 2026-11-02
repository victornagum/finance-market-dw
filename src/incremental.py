
import logging

from extract import PAGE_SIZE
from load_dw import load_dw
from load_raw import load_raw
from trading_pairs import get_active_trading_pairs

logger = logging.getLogger(__name__)

# Safety cap: 50 pages x 1000 candles per trading pair.
MAX_BATCHES = 50


def _run_pair_incremental(pair, max_batches):
    """Catch up one trading pair independently."""

    pair_key = pair["pair_key"]
    symbol = pair["symbol"]

    totals = {
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "processed": 0
    }

    batches = 0

    logger.info(
        "Starting incremental load: symbol=%s, pair_key=%s",
        symbol,
        pair_key
    )

    for batch in range(1, max_batches + 1):
        api_response_id, candle_count = load_raw(
            symbol=symbol,
            pair_key=pair_key
        )

        batches = batch

        if candle_count == 0:
            logger.info(
                "[%s] No new candles available. Pair is up to date.",
                symbol
            )
            break

        stats = load_dw(api_response_id)

        for key in totals:
            totals[key] += stats[key]

        logger.info(
            "[%s] Batch %s done: fetched=%s inserted=%s "
            "updated=%s unchanged=%s",
            symbol,
            batch,
            candle_count,
            stats["inserted"],
            stats["updated"],
            stats["unchanged"]
        )

        if candle_count < PAGE_SIZE:
            logger.info("[%s] Caught up.", symbol)
            break

        if stats["inserted"] == 0 and stats["updated"] == 0:
            logger.warning(
                "[%s] Full batch made no progress; stopping catch-up.",
                symbol
            )
            break

    else:
        logger.warning(
            "[%s] Reached max_batches=%s before catching up. "
            "The next run will continue.",
            symbol,
            max_batches
        )

    logger.info(
        "[%s] Incremental load finished: batches=%s "
        "inserted=%s updated=%s unchanged=%s processed=%s",
        symbol,
        batches,
        totals["inserted"],
        totals["updated"],
        totals["unchanged"],
        totals["processed"]
    )

    return totals


def run_incremental(max_batches=MAX_BATCHES):
    """Run incremental catch-up for every active trading pair."""

    pairs = get_active_trading_pairs()

    if not pairs:
        raise RuntimeError("No active trading pairs found.")

    logger.info(
        "Starting multi-pair incremental load: %s active pairs.",
        len(pairs)
    )

    grand_totals = {
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "processed": 0
    }

    for pair in pairs:
        stats = _run_pair_incremental(pair, max_batches)

        for key in grand_totals:
            grand_totals[key] += stats[key]

    logger.info(
        "Multi-pair incremental load finished: "
        "inserted=%s updated=%s unchanged=%s processed=%s",
        grand_totals["inserted"],
        grand_totals["updated"],
        grand_totals["unchanged"],
        grand_totals["processed"]
    )

    return grand_totals

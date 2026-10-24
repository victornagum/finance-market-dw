import logging

from extract import PAGE_SIZE
from load_dw import load_dw
from load_raw import load_raw

logger = logging.getLogger(__name__)

# Safety cap: 50 pages x 1000 candles is ~5.7 years of hourly data.
MAX_BATCHES = 50


def run_incremental(max_batches=MAX_BATCHES):
    """Load new closed candles, catching up after missed runs.

    Each loop is one full cycle: fetch -> save raw -> validate -> load warehouse.
    The next fetch starts from the newly stored latest candle, so progress is
    saved after every batch. If the pipeline stops midway, the next run simply
    continues from where it stopped.

    Stops when:
      - a batch is smaller than a full page (we reached the last closed candle),
      - a full batch changed nothing (no progress; avoids an endless loop), or
      - max_batches is reached (run again to continue).
    """
    totals = {"inserted": 0, "updated": 0, "unchanged": 0, "processed": 0}
    batches = 0

    for batch in range(1, max_batches + 1):
        api_response_id, candle_count = load_raw()
        stats = load_dw(api_response_id)
        batches = batch

        for key in totals:
            totals[key] += stats[key]

        logger.info("Batch %s done: fetched=%s inserted=%s updated=%s unchanged=%s",
                    batch, candle_count, stats["inserted"],
                    stats["updated"], stats["unchanged"])

        if candle_count < PAGE_SIZE:
            break  # caught up

        if stats["inserted"] == 0 and stats["updated"] == 0:
            logger.warning("Full batch made no progress; stopping catch-up.")
            break
    else:
        logger.warning("Reached max_batches=%s before catching up; "
                       "the next run will continue.", max_batches)

    logger.info("Incremental load finished: batches=%s inserted=%s updated=%s unchanged=%s",
                batches, totals["inserted"], totals["updated"], totals["unchanged"])
    return totals

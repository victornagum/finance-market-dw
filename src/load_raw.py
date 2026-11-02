
import logging

from extract import fetch_market_data
from raw_store import save_raw_response

logger = logging.getLogger(__name__)


def load_raw(symbol, pair_key):
    """Fetch market data for one trading pair and store the raw response.

    Returns (api_response_id, candle_count).
    """
    endpoint, params, data = fetch_market_data(
        symbol=symbol,
        pair_key=pair_key
    )

    api_response_id = save_raw_response(
        endpoint,
        params,
        data
    )

    logger.info(
        "API response saved: symbol=%s, pair_key=%s, "
        "ApiResponseID=%s, candles=%s",
        symbol,
        pair_key,
        api_response_id,
        len(data)
    )

    return api_response_id, len(data)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    # Temporary single-pair test.
    load_raw(symbol="BTCUSDT", pair_key=11)

import logging

from extract import fetch_market_data
from raw_store import save_raw_response

logger = logging.getLogger(__name__)


def load_raw():
    """Fetch from the API, store the raw response, return its ApiResponseID."""
    endpoint, params, data = fetch_market_data()
    api_response_id = save_raw_response(endpoint, params, data)
    logger.info("API response saved (ApiResponseID=%s, candles=%s).",
                api_response_id, len(data))
    return api_response_id


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    load_raw()

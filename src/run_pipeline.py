import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        # Rotates at ~1 MB, keeps 5 old files, so the log can't grow forever.
        RotatingFileHandler(LOG_DIR / "pipeline.log", maxBytes=1_000_000,
                            backupCount=5, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)
logger = logging.getLogger("pipeline")

# Imported AFTER logging is configured so module loggers use these handlers.
from load_dw import load_dw  # noqa: E402
from load_raw import load_raw  # noqa: E402


def main():
    try:
        logger.info("Starting: load_raw")
        api_response_id = load_raw()

        logger.info("Starting: load_dw")
        load_dw(api_response_id)  # process exactly the batch we just stored

        logger.info("Pipeline completed successfully!")
    except Exception:
        # Logged once, with traceback.
        logger.exception("Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

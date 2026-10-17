
import logging
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)

logger = logging.getLogger(__name__)



def run_step(script_name):
    logger.info("Starting: %s", script_name)

    process = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "src" / script_name)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        cwd=PROJECT_ROOT,
    )

    try:
        for line in process.stdout:
            message = line.rstrip()
            if message:
                logger.info("[%s] %s", script_name, message)

        return_code = process.wait()

        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, process.args)

        logger.info("Completed: %s", script_name)

    except Exception:
        process.kill()
        process.wait()
        logger.exception("Failed while running: %s", script_name)
        raise

def main():
    try:
        run_step("load_raw.py")
        run_step("load_dw.py")

        logger.info("Pipeline completed successfully!")

    except subprocess.CalledProcessError as error:
        logger.error("Pipeline failed with exit code %s", error.returncode)
        sys.exit(1)


if __name__ == "__main__":
    main()

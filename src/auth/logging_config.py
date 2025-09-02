import logging
import sys


def setup_logging() -> None:
    """Configure root logger with a simple structured format."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


logger = logging.getLogger("auth")
setup_logging()

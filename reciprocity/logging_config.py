from rich.console import Console
from rich.logging import RichHandler
from enum import Enum
import logging


class LogLevel(str, Enum):
    critical = "CRITICAL"
    error = "ERROR"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"


def setup_logging(level=LogLevel.info):
    console = Console(stderr=True)
    handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_level=True,
        show_path=False,
    )

    logging.basicConfig(
        level=level.value, handlers=[handler], force=True, format="%(message)s"
    )

    # Silence noisy deps
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("pytesseract").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

import logging

from .config import LOGGING_DATEFORMAT
from .config import LOGGING_FORMAT

try:
    from rich.logging import RichHandler

    handler = RichHandler(rich_tracebacks=True)
except ImportError:
    handler = logging.Handler()


logging.basicConfig(
    level=logging.DEBUG,
    format=LOGGING_FORMAT,
    datefmt=LOGGING_DATEFORMAT,
    handlers=[handler],
)

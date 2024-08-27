import logging
import sys

from .. import config

# from smpplib.command import logger as smpp_logger


# logger = logging.getLogger('SMPP client')


class ColorFormatter(logging.Formatter):
    COLORS = {
        'INFO': '\033[34m',
        'WARNING': '\033[01;33m',
        'ERROR': '\033[01;31m',
        'CRITICAL': '\033[02;47m\033[01;31m',
    }

    def format(self, record) -> str:
        prefix = self.COLORS.get(record.levelname)
        message = super().format(record)

        if prefix:
            message = f'{prefix}{message}\033[0m'

        return message


def setup_logging(logger: logging.Logger):
    env = config.ENVIRONMENT
    fmt = config.LOGGING_FORMAT
    datefmt = config.LOGGING_DATEFORMAT
    formatter = _get_formatter(env == 'local', fmt, datefmt)

    # application logger
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(config.LOGGING_LEVEL)

    # output logs to file in production
    if env == 'production':
        file_handler = logging.FileHandler('output.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # apply the same logging handlers to smpplib logging instances
    smpp_logger = logging.getLogger('smpplib.command')
    smpp_logger.handlers = logger.handlers
    smpp_logger.setLevel(config.SMPP_LOGGING_LEVEL)
    smpp_logger = logging.getLogger('smpp.Client')
    smpp_logger.handlers = logger.handlers
    smpp_logger.setLevel(config.SMPP_LOGGING_LEVEL)


def _get_formatter(is_local, fmt, datefmt):
    formatter_type = logging.Formatter
    if is_local and sys.stdout.isatty():
        formatter_type = ColorFormatter

    return formatter_type(
        fmt=fmt,
        datefmt=datefmt,
    )

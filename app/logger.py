import logging
import sys


def setup_logging():
    logger = logging.getLogger()

    log_format = logging.Formatter("[%(asctime)s] %(levelname)s : %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    if not logger.handlers:
        logger.addHandler(console_handler)

    logger.setLevel(logging.INFO)

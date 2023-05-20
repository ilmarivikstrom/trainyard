import logging


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    fmt = "%(asctime)s %(funcName)20s(): %(message)s"
    logging.basicConfig(level=log_level, format=fmt)
    return logging.getLogger()

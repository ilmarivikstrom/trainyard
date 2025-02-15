"""Phase: Exit."""

import sys

import pygame as pg

from src.config import Config
from src.utils.utils import setup_logging

logger = setup_logging(log_level=Config.LOG_LEVEL)


def exit_phase() -> None:
    logger.info("Exiting...")
    pg.quit()  # pylint: disable=no-member;
    sys.exit()

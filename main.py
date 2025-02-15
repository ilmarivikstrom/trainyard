"""Entry point."""

import pygame as pg

from src.config import Config
from src.utils.utils import setup_logging

logger = setup_logging(log_level=Config.LOG_LEVEL)


def main() -> None:
    _, _ = pg.init()
    from src.game_loop import GameLoop

    game_loop = GameLoop()
    game_loop.loop()


if __name__ == "__main__":
    main()

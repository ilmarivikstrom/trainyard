import pygame as pg

from src.config import Config
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


def main() -> None:
    _, _ = pg.init()  # pylint: disable=no-member;
    from src.game_loop import GameLoop  # pylint: disable=import-outside-toplevel;
    game_loop = GameLoop()
    game_loop.loop()


if __name__ == "__main__":
    main()

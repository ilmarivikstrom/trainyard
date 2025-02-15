"""Screen."""

import pygame as pg

from src.config import Config


class Screen:
    def __init__(self) -> None:
        self.width = Config.SCREEN_WIDTH
        self.height = Config.SCREEN_HEIGHT
        self.surface: pg.Surface = pg.display.set_mode(
            (self.width, self.height),
        )  # add flags=pg.NOFRAME for no-frame.

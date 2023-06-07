import pygame as pg

from src.config import Config
from src.utils import get_background_color_array

class Screen:
    def __init__(self) -> None:
        self.width = Config.screen_width
        self.height = Config.screen_height
        self.surface: pg.Surface = pg.display.set_mode((self.width, self.height)) # add flags=pg.NOFRAME for no-frame.
        self.background_color_array = get_background_color_array()

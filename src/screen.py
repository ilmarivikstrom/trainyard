import pygame as pg
from src.config import Config

class Screen:
    def __init__(self) -> None:
        self.width = Config.screen_width
        self.height = Config.screen_height
        self.surface: pg.Surface = pg.display.set_mode((self.width, self.height))

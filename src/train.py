import pygame as pg

from src.config import Config
from src.direction import Direction
from src.game_context import Resources


class Train(pg.sprite.Sprite):
    def __init__(self, i: int, j: int):
        super().__init__()
        self.i = i
        self.j = j
        self.image = Resources.train_surfaces["train0"]
        self.rect = self.image.get_rect()
        self.rect.x = i * Config.cell_size + Config.padding_x
        self.rect.y = j * Config.cell_size + Config.padding_y
        
        self.direction = Direction.RIGHT
        self.velocity = pg.Vector2(0, 0)
        self.on_track = False

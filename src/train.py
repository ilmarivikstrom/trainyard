import math
import pygame as pg

from src.config import Config
from src.direction import Direction


class Train(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, image: pg.Surface):
        super().__init__()
        self.i = i
        self.j = j
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = (i * Config.cell_size - 0.5 * Config.cell_size + Config.padding_x + 16)
        self.rect.y = (j * Config.cell_size + Config.padding_y + 16)
        self.pos = pg.Vector2(float(self.rect.x), float(self.rect.y))

        
        self.direction = Direction.RIGHT
        self.angle = 0 * math.pi / 2
        self.base_speed = 1
        self.velocity = pg.Vector2(1.0, 0.0)
        self.on_track = False
        self.at_endpoint = False
        self.last_collided_cells = []
        self.last_flipped_cell = None
        self.track_ahead = []
        self.selected_track = None

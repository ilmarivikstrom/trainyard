import pygame as pg
from src.config import Config

class DepartureStation(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, image: pg.Surface, angle: float = 0):
        super().__init__()
        self.i = i
        self.j = j
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = i * Config.cell_size + Config.padding_x
        self.rect.y = j * Config.cell_size + Config.padding_y

        self.angle = angle
        self.image = pg.transform.rotate(self.image, self.angle)


class ArrivalStation(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, image: pg.Surface, angle: float = 0):
        super().__init__()
        self.i = i
        self.j = j
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = i * Config.cell_size + Config.padding_x
        self.rect.y = j * Config.cell_size + Config.padding_y

        self.angle = angle
        self.image = pg.transform.rotate(self.image, self.angle)

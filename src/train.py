import math
from enum import Enum
from typing import List, Optional, Union

import pygame as pg

from src.cell import Cell
from src.field import EmptyCell
from src.config import Config
from src.direction import Direction
from src.resources import Graphics
from src.sound import Sound
from src.track import Track, StationTrack


class TrainColor(Enum):
    RED = "train_red"
    BLUE = "train_blue"
    YELLOW = "train_yellow"

    ORANGE = "train_orange"
    PURPLE = "train_purple"
    GREEN = "train_green"



class Train(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, color: TrainColor, direction: Direction = Direction.RIGHT):
        super().__init__()
        self.i = i
        self.j = j
        self.color = color
        self.direction = direction

        self.original_direction = direction

        self.image: pg.Surface = Graphics.img_surfaces[color.value]
        self.original_image: pg.Surface = self.image
        self.rect: pg.Rect = self.image.get_rect() # type: ignore
        self.rect.x = int(i * Config.cell_size - 0.5 * Config.cell_size + Config.padding_x + 48)
        self.rect.y = j * Config.cell_size + Config.padding_y + 16
        self.pos: pg.Vector2 = pg.Vector2(float(self.rect.x), float(self.rect.y))

        self.angle = 0 * math.pi / 2
        self.base_speed = 1
        self.on_track = False
        self.last_collided_cells: List[Cell] = []
        self.last_flipped_cell: Optional[EmptyCell] = None
        self.tracks_ahead: List[Union[Track, StationTrack]] = []
        self.selected_track: Optional[Track] = None
        self.is_reset = True
        self.original_pos = self.pos.copy()
        self.crashed = False


    def reset(self) -> None:
        self.pos = self.original_pos.copy()
        self.image = self.original_image
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        self.angle = 0
        self.direction = self.original_direction
        self.last_collided_cells = []
        self.last_flipped_cell = None
        self.is_reset = True


    def repaint(self, train_color: TrainColor) -> None:
        self.color = train_color
        self.image = Graphics.img_surfaces[self.color.value]
        self.original_image = self.image


    def rot_center(self, angle: float) -> pg.Surface:
        """rotate an image while keeping its center and size"""
        orig_rect = self.original_image.get_rect()
        rot_image = pg.transform.rotate(self.original_image, angle * 180 / math.pi)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image


    def move(self) -> None:
        self.image = self.rot_center(self.angle) # type: ignore
        self.pos.x = self.pos.x + self.base_speed * math.cos(self.angle)
        self.pos.y = self.pos.y - self.base_speed * math.sin(self.angle)
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        self.is_reset = False


    def tick(self, train_go: bool) -> None:
        if not self.on_track:
            self.base_speed = 0
        else:
            self.base_speed = 1
        if not train_go:
            self.reset()
        else:
            self.move()


    def crash(self) -> None:
        self.on_track = False
        self.selected_track = None
        self.crashed = True
        Sound.play_sound_on_channel(Sound.crash, 3)


    def add_last_collided_cell(self, empty_cell: Cell):
        self.last_collided_cells.append(empty_cell)
        self.last_collided_cells = self.last_collided_cells[-2:]

from typing import Optional

import pygame as pg

from src.cell import Cell
from src.config import Config

from src.resources import Resources
from src.saveable import SaveableAttributes
from src.train import TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)

class StationGoalSprite(pg.sprite.Sprite):
    def __init__(self, color: str, place: int, parent_rect: pg.Rect):
        super().__init__()
        self.image = Resources.img_surfaces[f"{color}_goal_{place}"]
        self.rect = parent_rect


class Station(Cell):
    def __init__(self, i: int, j: int, image: pg.Surface, angle: int, number_of_trains_left: int, train_color: TrainColor, block_short_char: str):
        super().__init__(i, j, image, angle)
        self.number_of_trains_left = number_of_trains_left
        self.train_color = train_color
        self.block_short_char = block_short_char
        self.original_number_of_trains = number_of_trains_left
        self.is_reset = False
        self.goals = []
        self.goal_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()
        self.last_release_tick: Optional[int] = None
        self.saveable_attributes = SaveableAttributes(block_type=self.block_short_char, color=self.train_color, number=self.number_of_trains_left, orientation=self.angle, position=(self.i, self.j))
        self.create_goal_sprites()

    def create_goal_sprites(self) -> None:
        if self.train_color == TrainColor.BLUE:
            goal_sprite_color = "blue"
        elif self.train_color == TrainColor.RED:
            goal_sprite_color = "red"
        elif self.train_color == TrainColor.YELLOW:
            goal_sprite_color = "yellow"
        elif self.train_color == TrainColor.ORANGE:
            goal_sprite_color = "orange"
        elif self.train_color == TrainColor.GREEN:
            goal_sprite_color = "green"
        elif self.train_color == TrainColor.PURPLE:
            goal_sprite_color = "purple"
        else:
            raise ValueError(f"Missing goal sprite string for color {self.train_color}")
        if self.rect: # Rect is Optional by design.
            self.goals = [StationGoalSprite(goal_sprite_color, i+1, self.rect) for i in range(self.number_of_trains_left)]
            self.goal_sprites.add(self.goals)

    def reset(self) -> None:
        if not self.is_reset:
            self.number_of_trains_left = self.original_number_of_trains
            self.goal_sprites.empty()
            self.create_goal_sprites()
            self.is_reset = True
            self.last_release_tick = None



class DepartureStation(Station):
    def __init__(self, i: int, j: int, angle: int, number_of_trains_left: int, train_color: TrainColor):
        super().__init__(i=i, j=j, image=Resources.img_surfaces["departure"], angle=angle, number_of_trains_left=number_of_trains_left, train_color=train_color, block_short_char="D")



class ArrivalStation(Station):
    def __init__(self, i: int, j: int, angle: int, number_of_trains_left: int, train_color: TrainColor):
        super().__init__(i=i, j=j, image=Resources.img_surfaces["arrival"], angle=angle, number_of_trains_left=number_of_trains_left, train_color=train_color, block_short_char="A")

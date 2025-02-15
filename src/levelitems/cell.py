"""Cell."""

from typing import TYPE_CHECKING

import pygame as pg

from src.config import Config
from src.coordinate import Coordinate
from src.direction import Direction
from src.user_control import UserControl
from src.utils.utils import setup_logging

if TYPE_CHECKING:
    from src.track import Track

logger = setup_logging(log_level=Config.log_level)

MAXIMUM_TRACKS = 2


class Cell(pg.sprite.Sprite):
    def __init__(
        self,
        pos: Coordinate,
        image: pg.Surface,
        angle: int,
    ) -> None:
        super().__init__()
        self.pos = pos
        self.angle = angle
        self.image = pg.transform.rotate(image, angle)
        self.rect: pg.Rect = self.image.get_rect()
        self.rect.x = self.pos.x * Config.cell_size + Config.padding_x
        self.rect.y = self.pos.y * Config.cell_size + Config.padding_y
        self.mouse_on = False
        self.cell_tracks: list[Track] = []

    def check_mouse_collision(self) -> bool:
        mouse_entered_this_cell = False
        if self.rect.collidepoint(UserControl.mouse_pos.as_tuple_float()):
            if not self.mouse_on:
                self.handle_mouse_cell_enter()
                mouse_entered_this_cell = True
            self.mouse_on = True
        else:
            self.mouse_on = False
        return mouse_entered_this_cell

    def detect_mouse_movement(
        self,
        prev_cell: Coordinate,
        curr_cell: Coordinate,
    ) -> Direction:
        if (curr_cell.x - prev_cell.x == 1) and (curr_cell.y == prev_cell.y):
            return Direction.RIGHT
        if (curr_cell.x - prev_cell.x == -1) and (curr_cell.y == prev_cell.y):
            return Direction.LEFT
        if (curr_cell.x == prev_cell.x) and (curr_cell.y - prev_cell.y == 1):
            return Direction.DOWN
        if (curr_cell.x == prev_cell.x) and (curr_cell.y - prev_cell.y == -1):
            return Direction.UP
        return Direction.NONE

    def handle_mouse_cell_enter(self) -> None:
        logger.info(f"Mouse entered cell: {self.pos}")
        UserControl.prev_cell = UserControl.curr_cell.copy()
        UserControl.curr_cell = Coordinate(self.pos.x, self.pos.y)
        UserControl.prev_movement = UserControl.curr_movement
        UserControl.curr_movement = self.detect_mouse_movement(
            UserControl.prev_cell,
            UserControl.curr_cell,
        )

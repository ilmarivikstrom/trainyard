from typing import List
import pygame as pg

from src.config import Config
from src.controls import UserControl
from src.direction import Direction
from src.resources import Resources
from src.sound import Sound
from src.track import Track
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)

class Cell(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, image: pg.Surface, angle: int):
        super().__init__()
        self.i = i
        self.j = j
        self.angle = angle
        self.image = pg.transform.rotate(image, angle)
        self.rect = self.image.get_rect()
        self.rect.x = i * Config.cell_size + Config.padding_x
        self.rect.y = j * Config.cell_size + Config.padding_y
        self.mouse_on = False

    def check_mouse_collision(self) -> bool:
        prev_cell_needs_checking = False
        if self.rect: # Rect is Optional by design.
            if self.rect.collidepoint(UserControl.mouse_pos):
                if not self.mouse_on:
                    self.handle_mouse_cell_enter()
                    prev_cell_needs_checking = True
                self.mouse_on = True
            else:
                self.mouse_on = False
        return prev_cell_needs_checking

    def handle_mouse_cell_enter(self) -> None:
        previous_cell = UserControl.curr_cell
        UserControl.prev_cell = previous_cell
        UserControl.curr_cell = pg.Vector2(self.i, self.j)
        UserControl.prev_movement = UserControl.curr_movement

        if (UserControl.curr_cell.x - UserControl.prev_cell.x == 1) and (
            UserControl.curr_cell.y == UserControl.prev_cell.y
        ):
            UserControl.curr_movement = Direction.RIGHT
        elif (
            UserControl.curr_cell.x - UserControl.prev_cell.x == -1
        ) and (UserControl.curr_cell.y == UserControl.prev_cell.y):
            UserControl.curr_movement = Direction.LEFT
        elif (UserControl.curr_cell.x == UserControl.prev_cell.x) and (
            UserControl.curr_cell.y - UserControl.prev_cell.y == 1
        ):
            UserControl.curr_movement = Direction.DOWN
        elif (UserControl.curr_cell.x == UserControl.prev_cell.x) and (
            UserControl.curr_cell.y - UserControl.prev_cell.y == -1
        ):
            UserControl.curr_movement = Direction.UP
        else:
            UserControl.curr_movement = Direction.NONE
            logger.info(
                f"Mouse warped. Prev: ({UserControl.prev_cell.x}, {UserControl.prev_cell.y}), current: ({UserControl.curr_cell.x}, {UserControl.curr_cell.y})"
                )


class EmptyCell(Cell):
    def __init__(self, i: int, j: int):
        super().__init__(i, j, Resources.img_surfaces["bg_tile"], 0)
        self.tracks: List[Track] = []

    def flip_tracks(self):
        if len(self.tracks) < 1:
            return
        for track in self.tracks:
            track.toggle_bright()
        self.tracks.reverse()
        Sound.play_sound_on_channel(Sound.track_flip, 2)

from typing import List
import pygame as pg

from src.config import Config
from src.user_control import UserControl
from src.direction import Direction
from src.graphics import Graphics
from src.saveable import SaveableAttributes
from src.sound import Sound
from src.track import Track, TrackType
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Cell(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, image: pg.Surface, angle: int, blocks_placement: bool):
        super().__init__()
        self.i = i
        self.j = j
        self.angle = angle
        self.image = pg.transform.rotate(image, angle)
        self.rect = self.image.get_rect()
        self.rect.x = i * Config.cell_size + Config.padding_x
        self.rect.y = j * Config.cell_size + Config.padding_y
        self.mouse_on = False
        self.tracks: List[Track] = []
        self.blocks_placement = blocks_placement

    def check_mouse_collision(self) -> bool:
        mouse_entered_this_cell = False
        if self.rect is None:
            return False
        if self.rect.collidepoint(UserControl.mouse_pos):
            if not self.mouse_on:
                self.handle_mouse_cell_enter()
                mouse_entered_this_cell = True
            self.mouse_on = True
        else:
            self.mouse_on = False
        return mouse_entered_this_cell

    def handle_mouse_cell_enter(self) -> None:
        logger.info(f"Mouse entered cell: {self.i, self.j}")
        if UserControl.curr_cell is None:
            raise ValueError("Current cell is None.")
        UserControl.prev_cell = UserControl.curr_cell.copy()
        UserControl.curr_cell = pg.Vector2(self.i, self.j)
        UserControl.prev_movement = UserControl.curr_movement
        if (UserControl.curr_cell.x - UserControl.prev_cell.x == 1) and (
            UserControl.curr_cell.y == UserControl.prev_cell.y
        ):
            UserControl.curr_movement = Direction.RIGHT
        elif (UserControl.curr_cell.x - UserControl.prev_cell.x == -1) and (
            UserControl.curr_cell.y == UserControl.prev_cell.y
        ):
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


class DrawingCell(Cell):
    def __init__(self, i: int, j: int):
        super().__init__(i, j, Graphics.img_surfaces["bg_tile"], 0, False)
        self.saveable_attributes = SaveableAttributes(block_type="E")

    def flip_tracks(self):
        if len(self.tracks) < 2:
            return
        track_types = [track.track_type for track in self.tracks]
        if (
            (TrackType.BOTTOM_LEFT in track_types and TrackType.TOP_RIGHT in track_types)
            or (TrackType.TOP_LEFT in track_types and TrackType.BOTTOM_RIGHT in track_types)
            or (TrackType.VERT in track_types and TrackType.HORI in track_types)
        ):
            return
        for track in self.tracks:
            track.toggle_bright()
        self.tracks.reverse()
        Sound.play_sound_on_any_channel(Sound.track_flip)


class RockCell(Cell):
    def __init__(self, i: int, j: int):
        super().__init__(i, j, Graphics.img_surfaces["rock"], 0, True)
        self.saveable_attributes = SaveableAttributes(block_type="R")

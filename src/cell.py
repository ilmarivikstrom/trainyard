from typing import List
import pygame as pg

from src.config import Config
from src.coordinate import Coordinate
from src.user_control import UserControl
from src.direction import Direction
from src.graphics import Graphics
from src.saveable import SaveableAttributes
from src.sound import Sound
from src.track import Track, TrackType
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Cell(pg.sprite.Sprite):
    def __init__(self, pos: Coordinate, image: pg.Surface, angle: int, blocks_placement: bool) -> None:
        super().__init__()
        self.pos = pos
        self.angle = angle
        self.image = pg.transform.rotate(image, angle)
        self.rect = self.image.get_rect()
        self.rect.x = self.pos.x * Config.cell_size + Config.padding_x
        self.rect.y = self.pos.y * Config.cell_size + Config.padding_y
        self.mouse_on = False
        self.tracks: List[Track] = []
        self.blocks_placement = blocks_placement

    def check_mouse_collision(self) -> bool:
        mouse_entered_this_cell = False
        if self.rect is None:
            return False
        if self.rect.collidepoint(UserControl.mouse_pos.as_tuple_float()):
            if not self.mouse_on:
                self.handle_mouse_cell_enter()
                mouse_entered_this_cell = True
            self.mouse_on = True
        else:
            self.mouse_on = False
        return mouse_entered_this_cell

    def detect_mouse_movement(self, prev_cell: Coordinate, curr_cell: Coordinate) -> Direction:
        if (curr_cell.x - prev_cell.x == 1) and (curr_cell.y == prev_cell.y):
            return Direction.RIGHT
        elif (curr_cell.x - prev_cell.x == -1) and (curr_cell.y == prev_cell.y):
            return Direction.LEFT
        elif (curr_cell.x == prev_cell.x) and (curr_cell.y - prev_cell.y == 1):
            return Direction.DOWN
        elif (curr_cell.x == prev_cell.x) and (curr_cell.y - prev_cell.y == -1):
            return Direction.UP
        else:
            return Direction.NONE

    def handle_mouse_cell_enter(self) -> None:
        logger.info(f"Mouse entered cell: {self.pos}")
        UserControl.prev_cell = UserControl.curr_cell.copy()
        UserControl.curr_cell = Coordinate(self.pos.x, self.pos.y)
        UserControl.prev_movement = UserControl.curr_movement
        UserControl.curr_movement = self.detect_mouse_movement(UserControl.prev_cell, UserControl.curr_cell)

class DrawingCell(Cell):
    def __init__(self, coords: Coordinate) -> None:
        super().__init__(coords, Graphics.img_surfaces["bg_tile"], 0, False)
        self.saveable_attributes = SaveableAttributes(block_type="E")

    def unflippable_tracks(self, track_types: List[TrackType]) -> bool:
        return (
            (TrackType.BOTTOM_LEFT in track_types and TrackType.TOP_RIGHT in track_types)
            or (TrackType.TOP_LEFT in track_types and TrackType.BOTTOM_RIGHT in track_types)
            or (TrackType.VERT in track_types and TrackType.HORI in track_types)
        )

    def flip_tracks(self) -> None:
        if len(self.tracks) < 2:
            return
        track_types = [track.track_type for track in self.tracks]
        if self.unflippable_tracks(track_types):
            return
        for track in self.tracks:
            track.toggle_bright()
        self.tracks.reverse()
        Sound.play_sound_on_any_channel(Sound.track_flip)


class RockCell(Cell):
    def __init__(self, coords: Coordinate) -> None:
        super().__init__(coords, Graphics.img_surfaces["rock"], 0, True)
        self.saveable_attributes = SaveableAttributes(block_type="R")

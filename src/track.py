from enum import Enum
from typing import Dict

import pygame as pg

from src.direction import Direction
from src.graphics import Graphics

class TrackType(Enum):
    VERT = 0
    HORI = 1
    TOP_RIGHT = 2
    TOP_LEFT = 3
    BOTTOM_LEFT = 4
    BOTTOM_RIGHT = 5

tracktype_to_direction = {
    TrackType.VERT: [Direction.UP, Direction.DOWN],
    TrackType.HORI: [Direction.RIGHT, Direction.LEFT],
    TrackType.TOP_RIGHT: [Direction.RIGHT, Direction.UP],
    TrackType.TOP_LEFT: [Direction.UP, Direction.LEFT],
    TrackType.BOTTOM_LEFT: [Direction.LEFT, Direction.DOWN],
    TrackType.BOTTOM_RIGHT: [Direction.RIGHT, Direction.DOWN]
}

angle_to_direction = {
    0: [Direction.RIGHT, Direction.LEFT],
    90: [Direction.UP, Direction.DOWN],
    180: [Direction.RIGHT, Direction.LEFT],
    270: [Direction.UP, Direction.DOWN]
}

class Track(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, cell_rect: pg.Rect, track_type: TrackType):
        super().__init__()
        self.i = i
        self.j = j
        self.cell_rect = cell_rect
        self.track_type = track_type
        self.directions = tracktype_to_direction[track_type]
        self.bright = True
        self.endpoints = [pg.Vector2(0, 0), pg.Vector2(0, 0)]
        self.images: Dict[str, pg.Surface] = {}

        if self.track_type == TrackType.VERT:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midbottom)]
            self.images["bright"] = pg.transform.rotate(Graphics.img_surfaces["track_s_bright"], Direction.UP.value)
            self.images["dark"] = pg.transform.rotate(Graphics.img_surfaces["track_s_dark"], Direction.UP.value)
            self.image = self.images["bright"]
        elif self.track_type == TrackType.HORI:
            self.endpoints = [pg.Vector2(self.cell_rect.midleft), pg.Vector2(self.cell_rect.midright)]
            self.images["bright"] = pg.transform.rotate(Graphics.img_surfaces["track_s_bright"], Direction.RIGHT.value)
            self.images["dark"] = pg.transform.rotate(Graphics.img_surfaces["track_s_dark"], Direction.RIGHT.value)
            self.image = self.images["bright"]
        elif self.track_type == TrackType.TOP_RIGHT:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midright)]
            self.images["bright"] = pg.transform.rotate(Graphics.img_surfaces["track_c_bright"], 90)
            self.images["dark"] = pg.transform.rotate(Graphics.img_surfaces["track_c_dark"], 90)
            self.image = self.images["bright"]
        elif self.track_type == TrackType.TOP_LEFT:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midleft)]
            self.images["bright"] = pg.transform.rotate(Graphics.img_surfaces["track_c_bright"], 180)
            self.images["dark"] = pg.transform.rotate(Graphics.img_surfaces["track_c_dark"], 180)
            self.image = self.images["bright"]
        elif self.track_type == TrackType.BOTTOM_LEFT:
            self.endpoints = [pg.Vector2(self.cell_rect.midleft), pg.Vector2(self.cell_rect.midbottom)]
            self.images["bright"] = pg.transform.rotate(Graphics.img_surfaces["track_c_bright"], 270)
            self.images["dark"] = pg.transform.rotate(Graphics.img_surfaces["track_c_dark"], 270)
            self.image = self.images["bright"]
        elif self.track_type == TrackType.BOTTOM_RIGHT:
            self.endpoints = [pg.Vector2(self.cell_rect.midbottom), pg.Vector2(self.cell_rect.midright)]
            self.images["bright"] = Graphics.img_surfaces["track_c_bright"]
            self.images["dark"] = Graphics.img_surfaces["track_c_dark"]
            self.image = self.images["bright"]
        else:
            raise ValueError("Track type not recognized.")

        self.rect = self.image.get_rect()
        self.rect.x = self.cell_rect.x
        self.rect.y = self.cell_rect.y

    def toggle_bright(self) -> None:
        self.bright = not self.bright
        if self.bright:
            self.image = self.images["bright"]
        else:
            self.image = self.images["dark"]



class StationTrack(Track):
    def __init__(self, i: int, j: int, parent_rect: pg.Rect, track_type: TrackType, angle: int):
        super().__init__(i, j, parent_rect, track_type)
        self.angle = angle
        self.parent_rect = parent_rect
        self.endpoints = [pg.Vector2(parent_rect.center)]

        if self.angle == 0:
            self.endpoints.append(pg.Vector2(self.parent_rect.midright))
        elif self.angle == 90:
            self.endpoints.append(pg.Vector2(self.parent_rect.midtop))
        elif self.angle == 180:
            self.endpoints.append(pg.Vector2(self.parent_rect.midleft))
        elif self.angle == 270:
            self.endpoints.append(pg.Vector2(self.parent_rect.midbottom))
        else:
            raise ValueError(f"StationTrack angle is wrong: {self.angle}. Expected from : [0, 90, 180, 270]")

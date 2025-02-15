"""Track."""

from __future__ import annotations

from enum import Enum

import pygame as pg

from src.coordinate import Coordinate
from src.direction import Direction
from src.graphics import Graphics

NAVIGATION_DOWN = [(0, 1)] * 64
NAVIGATION_UP = [(-navigation[0], -navigation[1]) for navigation in NAVIGATION_DOWN]

NAVIGATION_RIGHT = [(1, 0)] * 64
NAVIGATION_LEFT = [(-navigation[0], -navigation[1]) for navigation in NAVIGATION_RIGHT]

# Exactly 48 ticks long ellipse arc.
# NAVIGATION_RIGHTDOWN = [(1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,1), (1,0), (1,0), (1,0), (1,0), (1,1), (1,0), (1,0), (1,1), (1,0), (1,1), (1,0), (1,1), (1,0), (1,1), (1,1), (1,1), (1,1), (0,1), (1,1), (0,1), (1,1), (0,1), (1,1), (0,1), (0,1), (1,1), (0,1), (0,1), (0,1), (0,1), (1,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1)]
# Exactly 64 ticks long ellipse arc.
NAVIGATION_RIGHTDOWN = [
    (1, 0),
    (0, 0),
    (1, 0),
    (1, 0),
    (1, 0),
    (0, 0),
    (1, 0),
    (1, 0),
    (1, 0),
    (0, 0),
    (1, 0),
    (1, 1),
    (1, 0),
    (0, 0),
    (1, 0),
    (1, 0),
    (1, 0),
    (0, 0),
    (1, 1),
    (1, 0),
    (1, 0),
    (0, 0),
    (1, 1),
    (1, 0),
    (1, 1),
    (0, 0),
    (1, 0),
    (1, 1),
    (1, 0),
    (0, 0),
    (1, 1),
    (1, 1),
    (1, 1),
    (0, 0),
    (1, 1),
    (0, 1),
    (1, 1),
    (0, 0),
    (0, 1),
    (1, 1),
    (0, 1),
    (0, 0),
    (1, 1),
    (0, 1),
    (0, 1),
    (0, 0),
    (1, 1),
    (0, 1),
    (0, 1),
    (0, 0),
    (0, 1),
    (0, 1),
    (1, 1),
    (0, 0),
    (0, 1),
    (0, 1),
    (0, 1),
    (0, 0),
    (0, 1),
    (0, 1),
    (0, 1),
    (0, 0),
    (0, 1),
    (0, 1),
]
NAVIGATION_UPLEFT = [
    (-navigation[0], -navigation[1]) for navigation in NAVIGATION_RIGHTDOWN
][::-1]

NAVIGATION_RIGHTUP = [
    (navigation[0], -navigation[1]) for navigation in NAVIGATION_RIGHTDOWN
]
NAVIGATION_DOWNLEFT = [
    (-navigation[0], -navigation[1]) for navigation in NAVIGATION_RIGHTUP
][::-1]

NAVIGATION_LEFTDOWN = [
    (-navigation[0], navigation[1]) for navigation in NAVIGATION_RIGHTDOWN
]
NAVIGATION_UPRIGHT = [
    (-navigation[0], -navigation[1]) for navigation in NAVIGATION_LEFTDOWN
][::-1]

NAVIGATION_LEFTUP = [
    (-navigation[0], -navigation[1]) for navigation in NAVIGATION_RIGHTDOWN
]
NAVIGATION_DOWNRIGHT = [
    (-navigation[0], -navigation[1]) for navigation in NAVIGATION_LEFTUP
][::-1]


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
    TrackType.BOTTOM_RIGHT: [Direction.RIGHT, Direction.DOWN],
}

angle_to_direction = {
    0: [Direction.RIGHT, Direction.LEFT],
    90: [Direction.UP, Direction.DOWN],
    180: [Direction.RIGHT, Direction.LEFT],
    270: [Direction.UP, Direction.DOWN],
}


class Track(pg.sprite.Sprite):
    def __init__(
        self,
        coords: Coordinate,
        cell_rect: pg.Rect,
        track_type: TrackType,
    ) -> None:
        super().__init__()
        self.pos = coords
        self.cell_rect = cell_rect
        self.track_type = track_type
        self.directions: list[Direction] = tracktype_to_direction[track_type]
        self.bright = True
        self.endpoints = [Coordinate(0, 0), Coordinate(0, 0)]
        self.images: dict[str, pg.Surface] = {}

        self.navigation: list[tuple[int, int]] = []
        self.navigation_reversed: list[tuple[int, int]] = []

        if self.track_type == TrackType.VERT:
            self.endpoints = [
                Coordinate.from_tuple(self.cell_rect.midtop),
                Coordinate.from_tuple(self.cell_rect.midbottom),
            ]
            self.images["bright"] = pg.transform.rotate(
                Graphics.img_surfaces["track_s_bright"],
                Direction.UP.value,
            )
            self.images["dark"] = pg.transform.rotate(
                Graphics.img_surfaces["track_s_dark"],
                Direction.UP.value,
            )
            self.image = self.images["bright"]
            self.navigation = NAVIGATION_DOWN
            self.navigation_reversed = NAVIGATION_UP
        elif self.track_type == TrackType.HORI:
            self.endpoints = [
                Coordinate.from_tuple(self.cell_rect.midleft),
                Coordinate.from_tuple(self.cell_rect.midright),
            ]
            self.images["bright"] = pg.transform.rotate(
                Graphics.img_surfaces["track_s_bright"],
                Direction.RIGHT.value,
            )
            self.images["dark"] = pg.transform.rotate(
                Graphics.img_surfaces["track_s_dark"],
                Direction.RIGHT.value,
            )
            self.image = self.images["bright"]
            self.navigation = NAVIGATION_RIGHT
            self.navigation_reversed = NAVIGATION_LEFT
        elif self.track_type == TrackType.TOP_RIGHT:
            self.endpoints = [
                Coordinate.from_tuple(self.cell_rect.midtop),
                Coordinate.from_tuple(self.cell_rect.midright),
            ]
            self.images["bright"] = pg.transform.rotate(
                Graphics.img_surfaces["track_c_bright"],
                90,
            )
            self.images["dark"] = pg.transform.rotate(
                Graphics.img_surfaces["track_c_dark"],
                90,
            )
            self.image = self.images["bright"]
            self.navigation = NAVIGATION_DOWNRIGHT
            self.navigation_reversed = NAVIGATION_LEFTUP
        elif self.track_type == TrackType.TOP_LEFT:
            self.endpoints = [
                Coordinate.from_tuple(self.cell_rect.midtop),
                Coordinate.from_tuple(self.cell_rect.midleft),
            ]
            self.images["bright"] = pg.transform.rotate(
                Graphics.img_surfaces["track_c_bright"],
                180,
            )
            self.images["dark"] = pg.transform.rotate(
                Graphics.img_surfaces["track_c_dark"],
                180,
            )
            self.image = self.images["bright"]
            self.navigation = NAVIGATION_RIGHTUP
            self.navigation_reversed = NAVIGATION_DOWNLEFT
        elif self.track_type == TrackType.BOTTOM_LEFT:
            self.endpoints = [
                Coordinate.from_tuple(self.cell_rect.midleft),
                Coordinate.from_tuple(self.cell_rect.midbottom),
            ]
            self.images["bright"] = pg.transform.rotate(
                Graphics.img_surfaces["track_c_bright"],
                270,
            )
            self.images["dark"] = pg.transform.rotate(
                Graphics.img_surfaces["track_c_dark"],
                270,
            )
            self.image = self.images["bright"]
            self.navigation = NAVIGATION_RIGHTDOWN
            self.navigation_reversed = NAVIGATION_UPLEFT
        elif self.track_type == TrackType.BOTTOM_RIGHT:
            self.endpoints = [
                Coordinate.from_tuple(self.cell_rect.midbottom),
                Coordinate.from_tuple(self.cell_rect.midright),
            ]
            self.images["bright"] = Graphics.img_surfaces["track_c_bright"]
            self.images["dark"] = Graphics.img_surfaces["track_c_dark"]
            self.image = self.images["bright"]
            self.navigation = NAVIGATION_UPRIGHT
            self.navigation_reversed = NAVIGATION_LEFTDOWN
        else:
            msg = "Track type not recognized."
            raise ValueError(msg)

        self.rect = self.image.get_rect()
        self.rect.x = self.cell_rect.x
        self.rect.y = self.cell_rect.y

    def toggle_bright(self) -> None:
        self.bright = not self.bright
        if self.bright:
            self.image = self.images["bright"]
        else:
            self.image = self.images["dark"]


class InsideTrack(Track):
    def __init__(
        self,
        coords: Coordinate,
        parent_rect: pg.Rect,
        track_type: TrackType,
        angle: int,
    ) -> None:
        super().__init__(coords, parent_rect, track_type)
        self.angle = angle
        self.parent_rect = parent_rect
        self.endpoints = [Coordinate.from_tuple(parent_rect.center)]

        if self.angle == Direction.RIGHT.value:
            self.endpoints.append(Coordinate.from_tuple(self.parent_rect.midright))
        elif self.angle == Direction.UP.value:
            self.endpoints.append(Coordinate.from_tuple(self.parent_rect.midtop))
        elif self.angle == Direction.LEFT.value:
            self.endpoints.append(Coordinate.from_tuple(self.parent_rect.midleft))
        elif self.angle == Direction.DOWN.value:
            self.endpoints.append(Coordinate.from_tuple(self.parent_rect.midbottom))
        else:
            msg = (
                f"InsideTrack angle is not mappable to Direction. Angle: {self.angle}."
            )
            raise ValueError(
                msg,
            )

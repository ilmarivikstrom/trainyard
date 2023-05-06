from enum import Enum

import pygame as pg
import pygame.gfxdraw

from src.color_constants import GRAY, WHITE
from src.color_constants import *
from src.config import Config
from src.direction import Direction
from src.game_state import State


class TrackType(Enum):
    vert = 0
    hori = 1
    topright = 2
    topleft = 3
    bottomleft = 4
    bottomright = 5

tracktype_to_direction = {
    TrackType.vert: [Direction.UP, Direction.DOWN],
    TrackType.hori: [Direction.RIGHT, Direction.LEFT],
    TrackType.topright: [Direction.RIGHT, Direction.UP],
    TrackType.topleft: [Direction.UP, Direction.LEFT],
    TrackType.bottomleft: [Direction.LEFT, Direction.DOWN],
    TrackType.bottomright: [Direction.RIGHT, Direction.DOWN]
}


class Track:
    def __init__(self, i: int, j: int, cell_rect: pg.Rect, track_type: TrackType):
        self.i = i
        self.j = j
        self.cell_rect = cell_rect
        self.track_type = track_type
        self.directions = tracktype_to_direction[track_type]
        self.bright = True
        self.endpoints = pg.Vector2(0, 0)

        if self.track_type == TrackType.vert:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midbottom)]
        elif self.track_type == TrackType.hori:
            self.endpoints = [pg.Vector2(self.cell_rect.midleft), pg.Vector2(self.cell_rect.midright)]
        elif self.track_type == TrackType.topright:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midright)]
        elif self.track_type == TrackType.topleft:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midleft)]
        elif self.track_type == TrackType.bottomleft:
            self.endpoints = [pg.Vector2(self.cell_rect.midleft), pg.Vector2(self.cell_rect.midbottom)]
        elif self.track_type == TrackType.bottomright:
            self.endpoints = [pg.Vector2(self.cell_rect.midbottom), pg.Vector2(self.cell_rect.midright)]

    def toggle_bright(self):
        self.bright = not self.bright

    def draw(self):
        if self.bright == True:
            color = WHITE
        else:
            color = GRAY
        if self.track_type == TrackType.vert:
            pg.draw.line(State.screen_surface, color, self.cell_rect.midtop, self.cell_rect.midbottom)
        elif self.track_type == TrackType.hori:
            pg.draw.line(State.screen_surface, color, self.cell_rect.midleft, self.cell_rect.midright)
        elif self.track_type == TrackType.topright:
            pygame.gfxdraw.arc(State.screen_surface, self.cell_rect.right, self.cell_rect.top, int(Config.cell_size / 2), 90, 180, color)
        elif self.track_type == TrackType.topleft:
            pygame.gfxdraw.arc(State.screen_surface, self.cell_rect.left, self.cell_rect.top, int(Config.cell_size / 2), 0, 90, color)
        elif self.track_type == TrackType.bottomleft:
            pygame.gfxdraw.arc(State.screen_surface, self.cell_rect.left, self.cell_rect.bottom, int(Config.cell_size / 2), 270, 360, color)
        elif self.track_type == TrackType.bottomright:
            pygame.gfxdraw.arc(State.screen_surface, self.cell_rect.right, self.cell_rect.bottom, int(Config.cell_size / 2), 180, 270, color)
        
        for endpoint in self.endpoints:
            pygame.gfxdraw.pixel(State.screen_surface, int(endpoint.x), int(endpoint.y), RED1)

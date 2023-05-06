from enum import Enum

import pygame as pg
import pygame.gfxdraw

from src.color_constants import GRAY, RED1, WHITE
from src.config import Config
from src.direction import Direction
from src.game_state import State


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


class Track:
    def __init__(self, i: int, j: int, cell_rect: pg.Rect, track_type: TrackType):
        self.i = i
        self.j = j
        self.cell_rect = cell_rect
        self.track_type = track_type
        self.directions = tracktype_to_direction[track_type]
        self.bright = True
        self.endpoints = pg.Vector2(0, 0)

        if self.track_type == TrackType.VERT:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midbottom)]
        elif self.track_type == TrackType.HORI:
            self.endpoints = [pg.Vector2(self.cell_rect.midleft), pg.Vector2(self.cell_rect.midright)]
        elif self.track_type == TrackType.TOP_RIGHT:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midright)]
        elif self.track_type == TrackType.TOP_LEFT:
            self.endpoints = [pg.Vector2(self.cell_rect.midtop), pg.Vector2(self.cell_rect.midleft)]
        elif self.track_type == TrackType.BOTTOM_LEFT:
            self.endpoints = [pg.Vector2(self.cell_rect.midleft), pg.Vector2(self.cell_rect.midbottom)]
        elif self.track_type == TrackType.BOTTOM_RIGHT:
            self.endpoints = [pg.Vector2(self.cell_rect.midbottom), pg.Vector2(self.cell_rect.midright)]

    def toggle_bright(self):
        self.bright = not self.bright

    def draw(self):
        if self.bright == True:
            color = WHITE
        else:
            color = GRAY
        if self.track_type == TrackType.VERT:
            pg.draw.line(State.screen_surface, color, self.cell_rect.midtop, self.cell_rect.midbottom)
        elif self.track_type == TrackType.HORI:
            pg.draw.line(State.screen_surface, color, self.cell_rect.midleft, self.cell_rect.midright)
        elif self.track_type == TrackType.TOP_RIGHT:
            pygame.gfxdraw.arc(State.screen_surface, self.cell_rect.right, self.cell_rect.top, int(Config.cell_size / 2), 90, 180, color)
        elif self.track_type == TrackType.TOP_LEFT:
            pygame.gfxdraw.arc(State.screen_surface, self.cell_rect.left, self.cell_rect.top, int(Config.cell_size / 2), 0, 90, color)
        elif self.track_type == TrackType.BOTTOM_LEFT:
            pygame.gfxdraw.arc(State.screen_surface, self.cell_rect.left, self.cell_rect.bottom, int(Config.cell_size / 2), 270, 360, color)
        elif self.track_type == TrackType.BOTTOM_RIGHT:
            pygame.gfxdraw.arc(State.screen_surface, self.cell_rect.right, self.cell_rect.bottom, int(Config.cell_size / 2), 180, 270, color)
        
        for endpoint in self.endpoints:
            pygame.gfxdraw.pixel(State.screen_surface, int(endpoint.x), int(endpoint.y), RED1)

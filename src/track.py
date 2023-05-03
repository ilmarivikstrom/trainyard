from enum import Enum

import pygame as pg
import pygame.gfxdraw

from src.color_constants import GRAY, WHITE
from src.config import Config
from src.direction import Direction
from src.game_context import Ctx


class TrackType(Enum):
    vert = 0
    hori = 1
    topright = 2
    topleft = 3
    bottomleft = 4
    bottomright = 5

class Track:
    def __init__(self, i: int, j: int, rect: pg.Rect, track_type: TrackType):
        self.i = i
        self.j = j
        self.rect = rect
        self.track_type = track_type
        self.direction = tracktype_direction_mapping[track_type]
        self.bright = True

    def draw(self):
        if self.bright == True:
            color = WHITE
        else:
            color = GRAY
        if self.track_type == TrackType.vert:
            pg.draw.line(Ctx.screen_surface, color, self.rect.midtop, self.rect.midbottom)
        elif self.track_type == TrackType.hori:
            pg.draw.line(Ctx.screen_surface, color, self.rect.midleft, self.rect.midright)
        elif self.track_type == TrackType.topright:
            pygame.gfxdraw.arc(Ctx.screen_surface, self.rect.right, self.rect.top, int(Config.cell_size / 2), 90, 180, color)
        elif self.track_type == TrackType.topleft:
            pygame.gfxdraw.arc(Ctx.screen_surface, self.rect.left, self.rect.top, int(Config.cell_size / 2), 0, 90, color)
        elif self.track_type == TrackType.bottomleft:
            pygame.gfxdraw.arc(Ctx.screen_surface, self.rect.left, self.rect.bottom, int(Config.cell_size / 2), 270, 360, color)
        elif self.track_type == TrackType.bottomright:
            pygame.gfxdraw.arc(Ctx.screen_surface, self.rect.right, self.rect.bottom, int(Config.cell_size / 2), 180, 270, color)


tracktype_direction_mapping = {
    TrackType.vert: [Direction.UP, Direction.DOWN],
    TrackType.hori: [Direction.RIGHT, Direction.LEFT],
    TrackType.topright: [Direction.RIGHT, Direction.UP],
    TrackType.topleft: [Direction.UP, Direction.LEFT],
    TrackType.bottomleft: [Direction.LEFT, Direction.DOWN],
    TrackType.bottomright: [Direction.RIGHT, Direction.DOWN]
}
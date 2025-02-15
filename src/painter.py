"""Painter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.cell import Cell
from src.config import Config
from src.graphics import Graphics
from src.saveable import SaveableAttributes
from src.track import Track, TrackType
from src.utils import setup_logging

if TYPE_CHECKING:
    from src.coordinate import Coordinate
    from src.traincolor import TrainColor

logger = setup_logging(log_level=Config.log_level)


class Painter(Cell):
    def __init__(self, coords: Coordinate, angle: int, color: TrainColor) -> None:
        super().__init__(coords, Graphics.img_surfaces["painter"], angle)
        self.color = color
        self.saveable_attributes = SaveableAttributes(
            block_type="P",
            color=self.color,
            angle=self.angle,
        )

        if self.angle in [0, 180]:
            self.tracks: list[Track] = [Track(self.pos, self.rect, TrackType.HORI)]
        elif self.angle in [90, 270]:
            self.tracks: list[Track] = [Track(self.pos, self.rect, TrackType.VERT)]

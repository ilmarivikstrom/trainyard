"""Splitter."""

from src.cell import Cell
from src.config import Config
from src.coordinate import Coordinate
from src.graphics import Graphics
from src.saveable import SaveableAttributes
from src.track import InsideTrack, TrackType
from src.utils.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Splitter(Cell):
    def __init__(self, coords: Coordinate, angle: int) -> None:
        super().__init__(coords, Graphics.img_surfaces["splitter"], angle)
        self.saveable_attributes = SaveableAttributes(block_type="S", angle=self.angle)

        if self.angle in [0, 180]:
            self.cell_tracks.append(
                InsideTrack(self.pos, self.rect, TrackType.HORI, self.angle),
            )
            self.cell_tracks.append(
                InsideTrack(
                    self.pos,
                    self.rect,
                    TrackType.VERT,
                    (self.angle - 90) % 360,
                ),
            )
            self.cell_tracks.append(
                InsideTrack(
                    self.pos,
                    self.rect,
                    TrackType.VERT,
                    (self.angle + 90) % 360,
                ),
            )
        elif self.angle in [90, 270]:
            self.cell_tracks.append(
                InsideTrack(self.pos, self.rect, TrackType.VERT, self.angle),
            )
            self.cell_tracks.append(
                InsideTrack(
                    self.pos,
                    self.rect,
                    TrackType.HORI,
                    (self.angle - 90) % 360,
                ),
            )
            self.cell_tracks.append(
                InsideTrack(
                    self.pos,
                    self.rect,
                    TrackType.HORI,
                    (self.angle + 90) % 360,
                ),
            )

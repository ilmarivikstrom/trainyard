"""Splitter."""

from src.config import Config
from src.coordinate import Coordinate
from src.gfx.graphics import Graphics
from src.levelitems.cell import Cell
from src.saveable import SaveableAttributes
from src.track.track import InsideTrack, TrackType
from src.utils.utils import setup_logging

logger = setup_logging(log_level=Config.LOG_LEVEL)


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

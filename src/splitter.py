from src.cell import Cell
from src.config import Config
from src.graphics import Graphics
from src.saveable import SaveableAttributes
from src.track import InsideTrack, TrackType
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Splitter(Cell):
    def __init__(self, i: int, j: int, angle: int) -> None:
        super().__init__(i, j, Graphics.img_surfaces["splitter"], angle, True)
        self.saveable_attributes = SaveableAttributes(block_type="P", angle=self.angle)

        if self.rect is None:
            raise ValueError("Rect is None.")

        if self.angle in [0, 180]:
            self.tracks.append(InsideTrack(i, j, self.rect, TrackType.HORI, self.angle))
            self.tracks.append(InsideTrack(i, j, self.rect, TrackType.VERT, (self.angle - 90) % 360))
            self.tracks.append(InsideTrack(i, j, self.rect, TrackType.VERT, (self.angle + 90) % 360))
        elif self.angle in [90, 270]:
            self.tracks.append(InsideTrack(i, j, self.rect, TrackType.VERT, self.angle))
            self.tracks.append(InsideTrack(i, j, self.rect, TrackType.HORI, (self.angle - 90) % 360))
            self.tracks.append(InsideTrack(i, j, self.rect, TrackType.HORI, (self.angle + 90) % 360))

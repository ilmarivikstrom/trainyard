from typing import List

from src.cell import Cell
from src.config import Config
from src.coordinate import Coordinate
from src.graphics import Graphics
from src.saveable import SaveableAttributes
from src.track import Track, TrackType
from src.traincolor import TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Painter(Cell):
    def __init__(self, coords: Coordinate, angle: int, color: TrainColor) -> None:
        super().__init__(coords, Graphics.img_surfaces["painter"], angle, True)
        self.color = color
        self.saveable_attributes = SaveableAttributes(block_type="P", color=self.color, angle=self.angle)

        if self.rect is None:
            raise ValueError("Rect is None.")

        if self.angle in [0, 180]:
            self.tracks: List[Track] = [Track(self.pos, self.rect, TrackType.HORI)]
        elif self.angle in [90, 270]:
            self.tracks: List[Track] = [Track(self.pos, self.rect, TrackType.VERT)]

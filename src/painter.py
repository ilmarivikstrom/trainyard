from typing import List

from src.cell import Cell
from src.config import Config
from src.graphics import Graphics
from src.saveable import SaveableAttributes
from src.track import Track, TrackType
from src.traincolor import TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Painter(Cell):
    def __init__(self, i: int, j: int, angle: int, color: TrainColor) -> None:
        super().__init__(i, j, Graphics.img_surfaces["painter"], angle, True)
        self.color = color
        self.saveable_attributes = SaveableAttributes(block_type="P", color=self.color, angle=self.angle)

        if self.angle in [0, 180]:
            self.tracks: List[Track] = [
                Track(i, j, self.rect, TrackType.HORI)
            ]
        elif self.angle in [90, 270]:
            self.tracks: List[Track] = [
                Track(i, j, self.rect, TrackType.VERT)
            ]

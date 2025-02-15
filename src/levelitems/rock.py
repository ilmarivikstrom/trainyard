"""Rock."""

from src.coordinate import Coordinate
from src.gfx.graphics import Graphics
from src.levelitems.cell import Cell
from src.saveable import SaveableAttributes


class Rock(Cell):
    def __init__(self, coords: Coordinate) -> None:
        super().__init__(coords, Graphics.img_surfaces["rock"], 0)
        self.saveable_attributes = SaveableAttributes(block_type="R")

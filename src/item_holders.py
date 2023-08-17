from typing import List, Type, Union

import pygame as pg

from src.cell import Cell, DrawingCell, RockCell
from src.painter import Painter
from src.splitter import Splitter
from src.station import ArrivalStation, DepartureStation
from src.train import Train


class GridItemHolderBase:
    def __init__(self, item_type: Type[Union[Cell, Train]]) -> None:
        self.items: List[item_type] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: Cell) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def add_many(self, items: List[Cell]) -> None:
        for item in items:
            self.add_one(item)

    def remove_one(self, item: Cell) -> None:
        self.items.remove(item)
        self.sprites.remove(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()


class DrawingCellHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__(DrawingCell)


class RockHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__(RockCell)


class ArrivalHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__(ArrivalStation)


class DepartureHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__(DepartureStation)


class PainterHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__(Painter)


class SplitterHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__(Splitter)


class TrainHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__(Train)

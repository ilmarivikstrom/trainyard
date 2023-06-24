from typing import List

import pygame as pg

from src.cell import Cell, DrawingCell, RockCell
from src.painter import Painter
from src.splitter import Splitter
from src.station import ArrivalStation, DepartureStation
from src.train import Train


class GridItemHolderBase:
    def __init__(self) -> None:
        self.items: List[Cell] = []
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
        super().__init__()
        self.items: List[DrawingCell] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()


class RockHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[RockCell] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()


class ArrivalHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[ArrivalStation] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()


class DepartureHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[DepartureStation] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()


class PainterHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[Painter] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()


class SplitterHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[Splitter] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()


class TrainHolder(GridItemHolderBase):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[Train] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

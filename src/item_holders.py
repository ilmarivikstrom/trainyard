"""Item holders."""

from __future__ import annotations

import pygame as pg

from src.cell import DrawingCell, RockCell
from src.painter import Painter
from src.splitter import Splitter
from src.station import ArrivalStation, DepartureStation
from src.train import Train

GridItemTypeList = (
    DrawingCell
    | RockCell
    | ArrivalStation
    | DepartureStation
    | Painter
    | Splitter
    | Train
)
GridItemTypes = type[
    DrawingCell
    | RockCell
    | ArrivalStation
    | DepartureStation
    | Painter
    | Splitter
    | Train
]


# class GridItemHolderBase:
#     def __init__(self, item_type: type[Cell | Train]) -> None:
#         self.items: list[item_type] = []
#         self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

#     def add_one(self, item: GridItemTypeList) -> None:
#         self.items.append(item)
#         self.sprites.add(item)

#     def add_many(self, items: list[Cell]) -> None:
#         for item in items:
#             self.add_one(item)

#     def remove_one(self, item: GridItemTypeList) -> None:
#         self.items.remove(item)
#         self.sprites.remove(item)

#     def remove_all(self) -> None:
#         self.items.clear()
#         self.sprites.empty()


class DrawingCellHolder:
    def __init__(self) -> None:
        self.items: list[DrawingCell] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: DrawingCell) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()


class RockHolder:
    def __init__(self) -> None:
        self.items: list[RockCell] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: RockCell) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()


class ArrivalHolder:
    def __init__(self) -> None:
        self.items: list[ArrivalStation] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: ArrivalStation) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()


class DepartureHolder:
    def __init__(self) -> None:
        self.items: list[DepartureStation] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: DepartureStation) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()


class PainterHolder:
    def __init__(self) -> None:
        self.items: list[Painter] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: Painter) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()


class SplitterHolder:
    def __init__(self) -> None:
        self.items: list[Splitter] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: Splitter) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()


class TrainHolder:
    def __init__(self) -> None:
        self.items: list[Train] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: Train) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def remove_one(self, item: Train) -> None:
        self.items.remove(item)
        self.sprites.remove(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()

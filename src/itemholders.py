"""Item holders."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from src.levelitems.drawable import Drawable
    from src.levelitems.painter import Painter
    from src.levelitems.rock import Rock
    from src.levelitems.splitter import Splitter
    from src.levelitems.station import ArrivalStation, DepartureStation
    from src.train.train import Train


class DrawingCellHolder:
    def __init__(self) -> None:
        self.items: list[Drawable] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: Drawable) -> None:
        self.items.append(item)
        self.sprites.add(item)

    def remove_all(self) -> None:
        self.items.clear()
        self.sprites.empty()


class RockHolder:
    def __init__(self) -> None:
        self.items: list[Rock] = []
        self.sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

    def add_one(self, item: Rock) -> None:
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

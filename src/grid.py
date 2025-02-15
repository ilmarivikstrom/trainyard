"""Grid."""

from __future__ import annotations

from src.itemholders import (
    ArrivalHolder,
    DepartureHolder,
    DrawingCellHolder,
    PainterHolder,
    RockHolder,
    SplitterHolder,
    TrainHolder,
)
from src.levelitems.drawingcell import DrawingCell
from src.levelitems.painter import Painter
from src.levelitems.rock import Rock
from src.levelitems.splitter import Splitter
from src.levelitems.station import ArrivalStation, DepartureStation


class Grid:
    def __init__(self) -> None:
        self.rocks = RockHolder()
        self.drawing_cells = DrawingCellHolder()
        self.arrivals = ArrivalHolder()
        self.departures = DepartureHolder()
        self.painters = PainterHolder()
        self.splitters = SplitterHolder()
        self.trains = TrainHolder()

        self.all_items: list[
            Rock | DrawingCell | ArrivalStation | DepartureStation | Painter | Splitter
        ] = []

    def add(
        self,
        item: ArrivalStation
        | DepartureStation
        | Rock
        | DrawingCell
        | Painter
        | Splitter,
    ) -> None:
        if isinstance(item, ArrivalStation):
            self.arrivals.add_one(item)
            self.all_items.append(item)
        elif isinstance(item, DepartureStation):
            self.departures.add_one(item)
            self.all_items.append(item)
        elif isinstance(item, Rock):
            self.rocks.add_one(item)
            self.all_items.append(item)
        elif isinstance(item, DrawingCell):
            self.drawing_cells.add_one(item)
            self.all_items.append(item)
        elif isinstance(item, Painter):
            self.painters.add_one(item)
            self.all_items.append(item)
        elif isinstance(item, Splitter):  # type: ignore  # noqa: PGH003
            self.splitters.add_one(item)
            self.all_items.append(item)
        else:
            msg = f"Did not find a holder for item of type {type(item)}"
            raise TypeError(msg)

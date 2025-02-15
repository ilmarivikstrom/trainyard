"""Field."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

from src.cell import DrawingCell, RockCell
from src.color_constants import TY_TELLOW
from src.config import Config
from src.coordinate import Coordinate
from src.fieldborder import FieldBorder
from src.item_holders import (
    ArrivalHolder,
    DepartureHolder,
    DrawingCellHolder,
    PainterHolder,
    RockHolder,
    SplitterHolder,
    TrainHolder,
)
from src.painter import Painter
from src.saveable import Saveable
from src.splitter import Splitter
from src.station import ArrivalStation, DepartureStation
from src.track import Track, TrackType
from src.utils import setup_logging

if TYPE_CHECKING:
    from src.spark import Spark

logger = setup_logging(log_level=Config.log_level)


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
            RockCell
            | DrawingCell
            | ArrivalStation
            | DepartureStation
            | Painter
            | Splitter
        ] = []

    def add(
        self,
        item: ArrivalStation
        | DepartureStation
        | RockCell
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
        elif isinstance(item, RockCell):
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


class Field:
    def __init__(self, level: int = 0) -> None:
        self.level = level
        self.cells_x = Config.cells_x
        self.cells_y = Config.cells_y

        self.grid: Grid = Grid()

        self.num_crashed: int = 0
        self.is_released: bool = False
        self.current_tick: int = 0

        self.width_px = self.cells_x * Config.cell_size
        self.height_px = self.cells_y * Config.cell_size

        self.border: FieldBorder = FieldBorder(
            color=TY_TELLOW,
            topleft=(64, 128),
            width=self.width_px,
            height=self.height_px,
            thickness=1,
        )  # TODO: Field should have topleft coords and this should use them as well.

        self.sparks: list[Spark] = []

    def initialize_grid(self) -> None:
        with open(
            f"assets/levels/level_{self.level}.csv",
            newline="",
            encoding="utf-8",
        ) as level_file:
            level_reader = csv.reader(level_file, delimiter=";")
            for j, row in enumerate(level_reader):
                for i, item in enumerate(row[0].split("-")):
                    coords = Coordinate(i, j)
                    saveable = Saveable(item)
                    if saveable.type == "A":
                        arrival_station = ArrivalStation(
                            coords,
                            saveable.angle,
                            saveable.num_goals,
                            saveable.color,
                        )
                        self.grid.add(arrival_station)
                    elif saveable.type == "D":
                        departure_station = DepartureStation(
                            coords,
                            saveable.angle,
                            saveable.num_goals,
                            saveable.color,
                        )
                        self.grid.add(departure_station)
                    elif saveable.type == "E":
                        drawing_cell = DrawingCell(coords)
                        self.grid.add(drawing_cell)
                    elif saveable.type == "R":
                        rock_cell = RockCell(coords)
                        self.grid.add(rock_cell)
                    elif saveable.type == "P":
                        painter_cell = Painter(coords, saveable.angle, saveable.color)
                        self.grid.add(painter_cell)
                    elif saveable.type == "S":
                        splitter_cell = Splitter(coords, saveable.angle)
                        self.grid.add(splitter_cell)
                    else:
                        msg = f"Saveable type was unexpected: '{saveable.type}"
                        raise RuntimeError(
                            msg,
                        )

    def load_level(self, level: int) -> None:
        self.level = level
        self.clear()
        self.initialize_grid()

    def clear(self) -> None:
        self.grid.all_items.clear()

        self.grid.drawing_cells.remove_all()
        self.grid.rocks.remove_all()
        self.grid.arrivals.remove_all()
        self.grid.departures.remove_all()

        self.grid.trains.remove_all()
        self.grid.painters.remove_all()
        self.grid.splitters.remove_all()

        self.num_crashed: int = 0
        self.is_released: bool = False
        self.current_tick: int = 0

    def set_current_tick(self) -> None:
        if self.is_released:
            self.current_tick += 1
        else:
            self.current_tick = 0

    def reset(self) -> None:
        for departure_station in self.grid.departures.items:
            departure_station.reset()
        for arrival_station in self.grid.arrivals.items:
            arrival_station.reset()
        self.grid.trains.remove_all()
        self.num_crashed = 0
        self.is_released = False

    def get_grid_cell_list_index(self, i: int = 0, j: int = 0) -> int:
        return int(j) * self.cells_y + int(i)

    def get_grid_cell_at(
        self,
        i: int,
        j: int,
    ) -> (
        DrawingCell | RockCell | ArrivalStation | DepartureStation | Painter | Splitter
    ):
        return self.grid.all_items[self.get_grid_cell_list_index(i, j)]

    def _get_drawing_cell_at_indices(self, i: int, j: int) -> DrawingCell | None:
        cell = self.grid.all_items[self.get_grid_cell_list_index(i, j)]
        if not isinstance(cell, DrawingCell):
            return None
        return cell

    def get_drawing_cell_at_pos(self, pos: Coordinate) -> DrawingCell | None:
        return self._get_drawing_cell_at_indices(pos.x, pos.y)

    def insert_track_to_position(self, track_type: TrackType, pos: Coordinate) -> bool:
        drawing_cell = self.get_drawing_cell_at_pos(pos)
        if drawing_cell is None:
            logger.warning(
                f"Tried to insert track on a non-existing drawing cell at {pos}",
            )
            return False
        track_to_be_added = Track(pos, drawing_cell.rect, track_type)
        if track_type in [
            existing_track.track_type for existing_track in drawing_cell.cell_tracks
        ]:
            drawing_cell.cell_tracks.clear()
            drawing_cell.cell_tracks.append(track_to_be_added)
        else:
            drawing_cell.cell_tracks.append(track_to_be_added)
            drawing_cell.cell_tracks = drawing_cell.cell_tracks[-2:]
        if len(drawing_cell.cell_tracks) > 1:
            track_types = [track.track_type for track in drawing_cell.cell_tracks]
            if not (
                (
                    TrackType.BOTTOM_LEFT in track_types
                    and TrackType.TOP_RIGHT in track_types
                )
                or (
                    TrackType.TOP_LEFT in track_types
                    and TrackType.BOTTOM_RIGHT in track_types
                )
                or (TrackType.VERT in track_types and TrackType.HORI in track_types)
            ):
                drawing_cell.cell_tracks[0].bright = False
                drawing_cell.cell_tracks[0].image = drawing_cell.cell_tracks[0].images[
                    "dark"
                ]
        logger.info(f"Added track to pos {pos}")
        return True

"""Field."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

from src.color_constants import TY_TELLOW
from src.config import Config
from src.coordinate import Coordinate
from src.gfx.fieldborder import FieldBorder
from src.grid import Grid
from src.levelitems.drawable import Drawable
from src.levelitems.painter import Painter
from src.levelitems.rock import Rock
from src.levelitems.splitter import Splitter
from src.levelitems.station import ArrivalStation, DepartureStation
from src.saveable import Saveable
from src.track.track import Track, TrackType
from src.utils.utils import setup_logging

if TYPE_CHECKING:
    from src.gfx.spark import Spark

logger = setup_logging(log_level=Config.LOG_LEVEL)


class Field:
    def __init__(self, level: int = 0) -> None:
        self.level = level
        self.cells_x = Config.NUM_CELLS_X
        self.cells_y = Config.NUM_CELLS_Y

        self.grid: Grid = Grid()

        self.num_crashed: int = 0
        self.is_released: bool = False
        self.current_tick: int = 0

        self.width_px = self.cells_x * Config.CELL_SIZE
        self.height_px = self.cells_y * Config.CELL_SIZE

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
                        drawble = Drawable(coords)
                        self.grid.add(drawble)
                    elif saveable.type == "R":
                        rock_cell = Rock(coords)
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

        self.grid.drawbles.remove_all()
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
    ) -> Drawable | Rock | ArrivalStation | DepartureStation | Painter | Splitter:
        return self.grid.all_items[self.get_grid_cell_list_index(i, j)]

    def _get_drawble_at_indices(self, i: int, j: int) -> Drawable | None:
        cell = self.grid.all_items[self.get_grid_cell_list_index(i, j)]
        if not isinstance(cell, Drawable):
            return None
        return cell

    def get_drawble_at_pos(self, pos: Coordinate) -> Drawable | None:
        return self._get_drawble_at_indices(pos.x, pos.y)

    def insert_track_to_position(self, track_type: TrackType, pos: Coordinate) -> bool:
        drawble = self.get_drawble_at_pos(pos)
        if drawble is None:
            logger.warning(
                f"Tried to insert track on a non-existing drawing cell at {pos}",
            )
            return False
        track_to_be_added = Track(pos, drawble.rect, track_type)
        if track_type in [
            existing_track.track_type for existing_track in drawble.cell_tracks
        ]:
            drawble.cell_tracks.clear()
            drawble.cell_tracks.append(track_to_be_added)
        else:
            drawble.cell_tracks.append(track_to_be_added)
            drawble.cell_tracks = drawble.cell_tracks[-2:]
        if len(drawble.cell_tracks) > 1:
            track_types = [track.track_type for track in drawble.cell_tracks]
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
                drawble.cell_tracks[0].bright = False
                drawble.cell_tracks[0].image = drawble.cell_tracks[0].images["dark"]
        logger.info(f"Added track to pos {pos}")
        return True

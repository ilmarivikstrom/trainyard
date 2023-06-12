import csv
from typing import List, Optional, Union

import pygame as pg

from src.cell import DrawingCell, RockCell, Cell
from src.color_constants import TRAIN_YELLOW
from src.config import Config
from src.fieldborder import FieldBorder
from src.painter import Painter
from src.saveable import Saveable
from src.spark import Spark
from src.splitter import Splitter
from src.station import ArrivalStation, DepartureStation, Station
from src.track import Track, TrackType
from src.train import Train
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Field:
    def __init__(self, level: int = 0):
        self.level = level
        self.cells_x = Config.cells_x
        self.cells_y = Config.cells_y
        self.full_grid: List[Union[DrawingCell, RockCell, Station, Painter, Splitter]] = []
        self.drawing_cells: List[DrawingCell] = []
        self.rock_cells: List[RockCell] = []
        self.departure_stations: List[DepartureStation] = []
        self.arrival_stations: List[ArrivalStation] = []
        self.drawing_cells_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()
        self.rock_cells_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()
        self.departure_stations_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()
        self.arrival_stations_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

        self.painter_cells: List[Painter] = []
        self.painter_cells_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

        self.splitter_cells: List[Splitter] = []
        self.splitter_cells_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

        self.trains: List[Train] = []
        self.train_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

        self.num_crashed: int = 0
        self.is_released: bool = False
        self.current_tick: int = 0

        self.width_px = self.cells_x * Config.cell_size
        self.height_px = self.cells_y * Config.cell_size

        self.border: FieldBorder = FieldBorder(
            color=TRAIN_YELLOW, topleft=(54, 118), width=self.width_px, height=self.height_px, thickness=1
        )  # TODO: Field should have topleft coords and this guy should use them as well.

        self.sparks: List[Spark] = []

    def initialize_grid(self) -> None:
        with open(f"levels/level_{self.level}.csv", newline="", encoding="utf-8") as level_file:
            level_reader = csv.reader(level_file, delimiter=";")
            for j, row in enumerate(level_reader):
                for i, item in enumerate(row[0].split("-")):
                    saveable = Saveable(item)
                    if saveable.type == "A":
                        arrival_station = ArrivalStation(i, j, saveable.angle, saveable.num_goals, saveable.color)
                        self.full_grid.append(arrival_station)
                        self.arrival_stations_sprites.add(arrival_station)
                    elif saveable.type == "D":
                        departure_station = DepartureStation(i, j, saveable.angle, saveable.num_goals, saveable.color)
                        self.full_grid.append(departure_station)
                        self.departure_stations_sprites.add(departure_station)
                    elif saveable.type == "E":
                        drawing_cell = DrawingCell(i, j)
                        self.full_grid.append(drawing_cell)
                        self.drawing_cells_sprites.add(drawing_cell)
                    elif saveable.type == "R":
                        rock_cell = RockCell(i, j)
                        self.full_grid.append(rock_cell)
                        self.rock_cells_sprites.add(rock_cell)
                    elif saveable.type == "P":
                        painter_cell = Painter(i, j, saveable.angle, saveable.color)
                        self.full_grid.append(painter_cell)
                        self.painter_cells_sprites.add(painter_cell)
                    elif saveable.type == "S":
                        splitter_cell = Splitter(i, j, saveable.angle)
                        self.full_grid.append(splitter_cell)
                        self.splitter_cells_sprites.add(splitter_cell)
                    else:
                        raise ValueError(f"Saveable type was unexpected: '{saveable.type}")
        self.drawing_cells = [cell for cell in self.full_grid if isinstance(cell, DrawingCell)]
        self.rock_cells = [cell for cell in self.full_grid if isinstance(cell, RockCell)]
        self.departure_stations = [cell for cell in self.full_grid if isinstance(cell, DepartureStation)]
        self.arrival_stations = [cell for cell in self.full_grid if isinstance(cell, ArrivalStation)]
        self.painter_cells = [cell for cell in self.full_grid if isinstance(cell, Painter)]
        self.splitter_cells = [cell for cell in self.full_grid if isinstance(cell, Splitter)]

    def load_level(self, level: int) -> None:
        self.level = level
        self.clear()
        self.initialize_grid()

    def clear(self) -> None:
        self.full_grid.clear()
        self.drawing_cells.clear()
        self.rock_cells.clear()
        self.departure_stations.clear()
        self.arrival_stations.clear()
        self.drawing_cells_sprites.empty()
        self.rock_cells_sprites.empty()
        self.departure_stations_sprites.empty()
        self.arrival_stations_sprites.empty()
        self.trains.clear()
        self.train_sprites.empty()
        self.splitter_cells.clear()
        self.splitter_cells_sprites.empty()
        self.painter_cells.clear()
        self.painter_cells_sprites.empty()

        self.num_crashed: int = 0
        self.is_released: bool = False
        self.current_tick: int = 0

    def set_current_tick(self) -> None:
        if self.is_released:
            self.current_tick += 1
        else:
            self.current_tick = 0

    def reset(self) -> None:
        for departure_station in self.departure_stations:
            departure_station.reset()
        for arrival_station in self.arrival_stations:
            arrival_station.reset()
        self.trains.clear()
        self.train_sprites.empty()
        self.num_crashed = 0
        self.is_released = False

    def get_grid_cell_list_index(self, i: int = 0, j: int = 0) -> int:
        return int(j) * self.cells_y + int(i)

    def get_grid_cell_at(self, i: int, j: int) -> Union[DrawingCell, RockCell, Station, Painter, Splitter]:
        return self.full_grid[self.get_grid_cell_list_index(i, j)]

    def get_drawing_cell_at(self, i: int, j: int) -> Optional[DrawingCell]:
        cell = self.full_grid[self.get_grid_cell_list_index(i, j)]
        if not isinstance(cell, DrawingCell):
            return None
        return cell

    def insert_track_to_position(self, track_type: TrackType, pos: pg.Vector2) -> bool:
        drawing_cell = self.get_drawing_cell_at(round(pos.x), round(pos.y))
        if drawing_cell is None:
            logger.warning(f"Tried to insert track on a non-existing drawing cell at {pos}")
            return False
        if drawing_cell.rect is None:
            raise ValueError("Rect of drawing cell is None")
        track_to_be_added = Track(round(pos.x), round(pos.y), drawing_cell.rect, track_type)
        if track_type in [existing_track.track_type for existing_track in drawing_cell.tracks]:
            drawing_cell.tracks.clear()
            drawing_cell.tracks.append(track_to_be_added)
        else:
            drawing_cell.tracks.append(track_to_be_added)
            drawing_cell.tracks = drawing_cell.tracks[-2:]
        if len(drawing_cell.tracks) > 1:
            track_types = [track.track_type for track in drawing_cell.tracks]
            if not (
                (TrackType.BOTTOM_LEFT in track_types and TrackType.TOP_RIGHT in track_types)
                or (TrackType.TOP_LEFT in track_types and TrackType.BOTTOM_RIGHT in track_types)
                or (TrackType.VERT in track_types and TrackType.HORI in track_types)
            ):
                drawing_cell.tracks[0].bright = False
                drawing_cell.tracks[0].image = drawing_cell.tracks[0].images["dark"]
        logger.info(f"Added track to pos {pos}")
        return True

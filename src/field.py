import csv
from typing import List, Union

import pygame as pg

from src.cell import EmptyCell, RockCell
from src.color_constants import TRAIN_YELLOW
from src.config import Config
from src.fieldborder import FieldBorder
from src.saveable import Saveable
from src.station import ArrivalStation, DepartureStation, Station
from src.track import Track, TrackType
from src.train import Train
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Field:
    def __init__(self, level: int=0):
        self.level = level
        self.cells_x = Config.cells_x
        self.cells_y = Config.cells_y
        self.full_grid: List[Union[EmptyCell, RockCell, Station]] = []
        self.empty_cells: List[EmptyCell] = []
        self.rock_cells: List[RockCell] = []
        self.departure_stations: List[DepartureStation] = []
        self.arrival_stations: List[ArrivalStation] = []
        self.empty_cells_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()
        self.rock_cells_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()
        self.departure_stations_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()
        self.arrival_stations_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

        self.trains: List[Train] = []
        self.train_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()

        self.num_crashed: int = 0
        self.is_released: bool = False
        self.current_tick: int = 0

        self.width_px = self.cells_x * Config.cell_size
        self.height_px = self.cells_y * Config.cell_size

        self.border = FieldBorder(color=TRAIN_YELLOW, topleft=(64, 128), width=self.width_px, height=self.height_px, thickness=1)


    def initialize_grid(self) -> None:
        with open(f"levels/level_{self.level}.csv", newline="", encoding="utf-8") as level_file:
            level_reader = csv.reader(level_file, delimiter=";")
            for j, row in enumerate(level_reader):
                for i, item in enumerate(row[0].split("-")):
                    saveable = Saveable(item)
                    if saveable.type == "A":
                        arrival_station = ArrivalStation(i, j, saveable.angle, saveable.num_goals, saveable.color_goals)
                        self.full_grid.append(arrival_station)
                        self.arrival_stations_sprites.add(arrival_station)
                    elif saveable.type == "D":
                        departure_station = DepartureStation(i, j, saveable.angle, saveable.num_goals, saveable.color_goals)
                        self.full_grid.append(departure_station)
                        self.departure_stations_sprites.add(departure_station)
                    elif saveable.type == "E":
                        empty_cell = EmptyCell(i, j)
                        self.full_grid.append(empty_cell)
                        self.empty_cells_sprites.add(empty_cell)
                    elif saveable.type == "R":
                        rock_cell = RockCell(i, j)
                        self.full_grid.append(rock_cell)
                        self.rock_cells_sprites.add(rock_cell)
                    else:
                        raise ValueError(f"Saveable type was unexpected: '{saveable.type}")
        self.empty_cells = [cell for cell in self.full_grid if isinstance(cell, EmptyCell)]
        self.rock_cells = [cell for cell in self.full_grid if isinstance(cell, RockCell)]
        self.departure_stations = [cell for cell in self.full_grid if isinstance(cell, DepartureStation)]
        self.arrival_stations = [cell for cell in self.full_grid if isinstance(cell, ArrivalStation)]


    def load_level(self, level: int) -> None:
        self.level = level
        self.clear()
        self.initialize_grid()


    def clear(self) -> None:
        self.full_grid.clear()
        self.empty_cells.clear()
        self.rock_cells.clear()
        self.departure_stations.clear()
        self.arrival_stations.clear()
        self.empty_cells_sprites.empty()
        self.rock_cells_sprites.empty()
        self.departure_stations_sprites.empty()
        self.arrival_stations_sprites.empty()
        self.trains.clear()
        self.train_sprites.empty()

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


    def get_grid_cell_at(self, i: int, j: int) -> Union[EmptyCell, RockCell, Station]:
        return self.full_grid[self.get_grid_cell_list_index(i, j)]


    def insert_track_to_position(
            self,
            track_type: TrackType,
            pos: pg.Vector2
    ) -> None:
        grid_cell = self.get_grid_cell_at(round(pos.x), round(pos.y))
        if grid_cell.blocks_placement:
            return
        if grid_cell.rect is None:
            raise ValueError("Rect of empty_cell is None")
        track_to_be_added = Track(round(pos.x), round(pos.y), grid_cell.rect, track_type)
        if track_type in [existing_track.track_type for existing_track in grid_cell.tracks]:
            grid_cell.tracks.clear()
            grid_cell.tracks.append(track_to_be_added)
        else:
            grid_cell.tracks.append(track_to_be_added)
            grid_cell.tracks = grid_cell.tracks[-2:]
        if len(grid_cell.tracks) > 1:
            grid_cell.tracks[0].bright = False
            grid_cell.tracks[0].image = grid_cell.tracks[0].images["dark"]
        logger.info(f"Added track to pos {pos}")

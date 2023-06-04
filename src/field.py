import csv
from typing import List, Union

import pygame as pg

from src.cell import EmptyCell, RockCell
from src.config import Config
from src.saveable import Saveable
from src.station import ArrivalStation, DepartureStation, Station
from src.track import Track, TrackType
from src.train import Train
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Field:
    def __init__(self):
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


    def initialize_grid(self, file_name: str="level_0.csv") -> None:
        with open(f"levels/{file_name}", newline="", encoding="utf-8") as level_file:
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


    def get_grid_cell_list_index(self, i: int = 0, j: int = 0) -> int:
        return int(j) * self.cells_y + int(i)

    def get_grid_cell_at(self, i: int, j: int) -> Union[EmptyCell, Station]:
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

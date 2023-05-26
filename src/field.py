from typing import List

import pygame as pg

from src.cell import EmptyCell
from src.config import Config
from src.direction import Direction
from src.game_state import State
from src.station import ArrivalStation, DepartureStation, Station
from src.track import Track, TrackType
from src.train import TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Field:
    def __init__(self):
        self.cells_x = Config.cells_x
        self.cells_y = Config.cells_y
        self.empty_cells: List[EmptyCell] = []
        self.empty_cells_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()
        self.stations: List[Station] = []
        self.stations_sprites: pg.sprite.Group[pg.sprite.Sprite] = pg.sprite.Group()


    def initialize_grid(self) -> None:
        for j in range(0, self.cells_y):
            for i in range(0, self.cells_x):
                empty_cell = EmptyCell(i, j)
                self.empty_cells.append(empty_cell)


    def add_level_objects(self) -> None:
        for j in range(0, self.cells_y):
            for i in range(0, self.cells_x):
                # Add some stations. Manually, for now...
                if (i,j) == (1,1):
                    self.stations.append(DepartureStation(i=i, j=j, angle=Direction.DOWN.value, number_of_trains_left=4, train_color=TrainColor.YELLOW))
                elif (i,j) == (3,1):
                    self.stations.append(DepartureStation(i=i, j=j, angle=Direction.DOWN.value, number_of_trains_left=4, train_color=TrainColor.BLUE))
                elif (i,j) == (4,1):
                    self.stations.append(DepartureStation(i=i, j=j, angle=Direction.DOWN.value, number_of_trains_left=1, train_color=TrainColor.BLUE))
                elif (i,j) == (6,1):
                    self.stations.append(DepartureStation(i=i, j=j, angle=Direction.DOWN.value, number_of_trains_left=1, train_color=TrainColor.RED))
                elif (i,j) == (3,6):
                    self.stations.append(DepartureStation(i=i, j=j, angle=Direction.UP.value, number_of_trains_left=3, train_color=TrainColor.YELLOW))
                elif (i,j) == (5,6):
                    self.stations.append(DepartureStation(i=i, j=j, angle=Direction.UP.value, number_of_trains_left=3, train_color=TrainColor.RED))
                elif (i,j) == (0,4):
                    self.stations.append(ArrivalStation(i=i, j=j, angle=Direction.RIGHT.value, number_of_trains_left=4, train_color=TrainColor.GREEN))
                elif (i,j) == (7,4):
                    self.stations.append(ArrivalStation(i=i, j=j, angle=Direction.LEFT.value, number_of_trains_left=1, train_color=TrainColor.PURPLE))
                elif (i,j) == (4,7):
                    self.stations.append(ArrivalStation(i=i, j=j, angle=Direction.UP.value, number_of_trains_left=3, train_color=TrainColor.ORANGE))
        self.empty_cells_sprites.add(self.empty_cells)
        self.stations_sprites.add(self.stations)

    def _get_empty_cell_index(self, i: int = 0, j: int = 0) -> int:
        return int(j) * self.cells_y + int(i)

    def get_empty_cell_at(self, i: int, j: int) -> EmptyCell:
        return self.empty_cells[self._get_empty_cell_index(i, j)]

    def place_track_item(
            self,
            requested_tracktype: TrackType,
            pos: pg.Vector2
    ) -> None:
        logger.info("Called set_grid_track_item")
        empty_cell = self.get_empty_cell_at(round(pos.x), round(pos.y))
        if empty_cell.rect:
            track_to_be_added = Track(round(pos.x), round(pos.y), empty_cell.rect, requested_tracktype)
            if requested_tracktype in [existing_track.track_type for existing_track in empty_cell.tracks]:
                empty_cell.tracks.clear()
                empty_cell.tracks.append(track_to_be_added)
            else:
                empty_cell.tracks.append(track_to_be_added)
                empty_cell.tracks = empty_cell.tracks[-2:]
            if len(empty_cell.tracks) > 1:
                empty_cell.tracks[0].bright = False
                empty_cell.tracks[0].image = empty_cell.tracks[0].images["dark"]
            State.prev_cell_needs_checking = False

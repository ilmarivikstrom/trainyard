import pygame as pg

from src.cell import Empty
from src.config import Config
from src.direction import Direction
from src.game_state import State
from src.station import ArrivalStation, DepartureStation
from src.track import Track, TrackType
from src.train import TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Field:
    def __init__(self):
        self.cells_x = Config.cells_x
        self.cells_y = Config.cells_y
        self.width_px = self.cells_x * Config.cell_size
        self.height_px = self.cells_y * Config.cell_size
        self.grid = []

    def initialize_grid(self) -> None:
        for j in range(0, self.cells_y):
            for i in range(0, self.cells_x):
                empty_cell = Empty(i, j)
                self.grid.append(empty_cell)
                State.cell_sprites.add(empty_cell)
                # Add some stations. Manually, for now...
                if (i,j) == (2,2):
                    State.departure_stations.append(DepartureStation(i=i, j=j, angle=Direction.UP.value, number_of_trains=4, train_color=TrainColor.YELLOW))
                    State.departure_station_sprites.add(State.departure_stations)
                elif (i,j) == (5,2):
                    State.departure_stations.append(DepartureStation(i=i, j=j, angle=Direction.DOWN.value, number_of_trains=4, train_color=TrainColor.YELLOW))
                    State.departure_station_sprites.add(State.departure_stations)
                elif (i,j) == (6,6):
                    State.arrival_station = ArrivalStation(i=i, j=j, angle=Direction.DOWN.value, number_of_trains=3, train_color=TrainColor.YELLOW)
                    State.arrival_station_sprites.add(State.arrival_station)

    def _get_cell_index(self, i: int = 0, j: int = 0) -> int:
        return int(j) * self.cells_y + int(i)

    def get_cell_at(self, i: int, j: int):
        return self.grid[self._get_cell_index(i, j)]

    def place_track_item(
            self,
            requested_tracktype: TrackType,
            pos: pg.Vector2
    ) -> None:
        logger.info("Called set_grid_track_item")
        cell = self.get_cell_at(pos.x, pos.y)
        track_to_be_added = Track(pos.x, pos.y, cell.rect, requested_tracktype)
        if requested_tracktype in [existing_track.track_type for existing_track in cell.tracks]:
            cell.tracks.clear()
            cell.tracks.append(track_to_be_added)
        else:
            cell.tracks.append(track_to_be_added)
            cell.tracks = cell.tracks[-2:]
        if len(cell.tracks) > 1:
            cell.tracks[0].bright = False
            cell.tracks[0].image = cell.tracks[0].images["dark"]
        State.prev_cell_needs_checking = False

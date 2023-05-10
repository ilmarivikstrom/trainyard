import pygame as pg

from src.cell import Cell
from src.color_constants import colors
from src.config import Config
from src.direction import Direction
from src.game_state import State
from src.station import ArrivalStation, DepartureStation
from src.track import Track, TrackType
from src.train import TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")


class Field:
    cells_x = Config.cells_x
    cells_y = Config.cells_y
    width_px = cells_x * Config.cell_size
    height_px = cells_y * Config.cell_size
    grid = []

    @staticmethod
    def initialize_grid() -> None:
        for j in range(0, Field.cells_y):
            for i in range(0, Field.cells_x):
                cell = Cell(i, j, pg.Color(colors["gray15"]))
                Field.grid.append(cell)
                State.cell_sprites.add(cell)
        # Manually set the locations... for now...
        State.departure_station = DepartureStation(i=3, j=3, angle=Direction.UP.value, number_of_trains_to_release=4, train_color=TrainColor.BLUE)
        State.arrival_station = ArrivalStation(i=5, j=5, angle=Direction.DOWN.value, number_of_trains_to_catch=4, train_color=TrainColor.BLUE)
        State.departure_station_sprites.add(State.departure_station)
        State.arrival_station_sprites.add(State.arrival_station)


    @staticmethod
    def _get_cell_index(i: int = 0, j: int = 0) -> int:
        return int(j) * Field.cells_y + int(i)

    @staticmethod
    def get_cell_at(i: int, j: int):
        return Field.grid[Field._get_cell_index(i, j)]

    @staticmethod
    def place_track_item(
        requested_tracktype: TrackType, pos: pg.Vector2
    ) -> None:
        logger.info("Called set_grid_track_item")
        cell = Field.get_cell_at(pos.x, pos.y)
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

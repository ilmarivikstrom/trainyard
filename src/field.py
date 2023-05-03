import pygame as pg

from src.cell import Cell
from src.color_constants import colors
from src.config import Config
from src.game_context import Ctx, Direction
from src.track import Track, TrackType
from src.train import Train
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")




class Field:
    cells_x = Config.cells_x
    cells_y = Config.cells_y
    width_px = cells_x * Config.cell_size
    height_px = cells_y * Config.cell_size
    grid = []

    def initialize_grid() -> None:
        for j in range(0, Field.cells_y):
            for i in range(0, Field.cells_x):
                cell = Cell(i, j, pg.Color(colors["gray15"]))
                Field.grid.append(cell)
                Ctx.cell_sprites.add(cell)
        Ctx.train = Train(1, 1)
        Ctx.train_sprites.add(Ctx.train)


    def _get_cell_index(i: int = 0, j: int = 0) -> int:
        return int(j) * Field.cells_y + int(i)

    def get_cell_at(i: int, j: int):
        return Field.grid[Field._get_cell_index(i, j)]


def place_track_item(
    requested_tracktype: TrackType, pos: pg.Vector2
) -> None:
    logger.info("Called set_grid_track_item")
    cell = Field.get_cell_at(pos.x, pos.y)
    track_to_be_added = Track(pos.x, pos.y, cell.rect, requested_tracktype)
    if requested_tracktype in [existing_track.track_type for existing_track in cell.tracks]:
        cell.tracks = [track_to_be_added]
    else:
        cell.tracks.append(track_to_be_added)
        cell.tracks = cell.tracks[-2:]
    if len(cell.tracks) > 1:
        cell.tracks[0].bright = False
    Ctx.prev_cell_needs_checking = False

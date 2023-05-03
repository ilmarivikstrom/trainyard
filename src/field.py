import pygame as pg
from typing import Tuple, List
from src.config import Config
from src.utils import setup_logging
from src.color_constants import colors
from src.game_context import Ctx, Direction, Resources

logger = setup_logging(log_level="DEBUG")


class Cell:
    def __init__(self, i: int, j: int, color: pg.Color, line_width: int = 1):
        self.i = i
        self.j = j
        self.base_rect = pg.Rect(
            i * Config.cell_size + Config.padding_x,
            j * Config.cell_size + Config.padding_y,
            Config.cell_size,
            Config.cell_size,
        )
        self.color = color
        self.line_width = line_width
        self.activated = False
        self.mouse_on = False
        self.track_items = []

    def activate(self):
        if not self.activated:
            logger.debug(f"Activating Cell at {(self.i, self.j)}")
            self.activated = True
            self.color = pg.Color(colors["gray30"])
            self.line_width = 1

    def deactivate(self):
        if self.activated:
            logger.debug(f"Deactivating Cell at {(self.i, self.j)}")
            self.activated = False
            self.color = pg.Color(colors["gray15"])
            self.line_width = 1

    def mouse_enter(self):
        if not self.mouse_on:
            logger.debug(f"Mouse entered Cell at {(self.i, self.j)}")
            self.mouse_on = True
            handle_mouse_cell_enter(self)

    def mouse_exit(self):
        if self.mouse_on:
            self.mouse_on = False


def handle_mouse_cell_enter(cell) -> None:
    previous_cell = Ctx.curr_cell
    Ctx.prev_cell_needs_checking = True
    Ctx.prev_cell = previous_cell
    Ctx.curr_cell = pg.Vector2(cell.i, cell.j)
    Ctx.prev_movement = Ctx.curr_movement

    if (
        Ctx.prev_cell is None
        or Ctx.prev_cell.x is None
        or Ctx.prev_cell.y is None
    ):
        logger.warn("Previous mouse cell was None. Returning from mouse handling.")
        return
    if (Ctx.curr_cell.x - Ctx.prev_cell.x == 1) and (
        Ctx.curr_cell.y == Ctx.prev_cell.y
    ):
        Ctx.curr_movement = Direction.RIGHT
    elif (
        Ctx.curr_cell.x - Ctx.prev_cell.x == -1
    ) and (Ctx.curr_cell.y == Ctx.prev_cell.y):
        Ctx.curr_movement = Direction.LEFT
    elif (Ctx.curr_cell.x == Ctx.prev_cell.x) and (
        Ctx.curr_cell.y - Ctx.prev_cell.y == 1
    ):
        Ctx.curr_movement = Direction.DOWN
    elif (Ctx.curr_cell.x == Ctx.prev_cell.x) and (
        Ctx.curr_cell.y - Ctx.prev_cell.y == -1
    ):
        Ctx.curr_movement = Direction.UP
    else:
        Ctx.curr_movement = None
        logger.info(
            f"Mouse warped. Prev: ({Ctx.prev_cell.x}, {Ctx.prev_cell.y}), current: ({Ctx.curr_cell.x}, {Ctx.curr_cell.y})"
        )


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

    def place_track_item(
        track_item: Tuple[pg.Surface, List[Direction]], pos: pg.Vector2
    ) -> None:
        logger.info("Called set_grid_track_item")
        cell = Field.grid[Field.get_cell_index(pos.x, pos.y)]
        if track_item in cell.track_items:
            cell.track_items = [track_item]
        else:
            cell.track_items.append(track_item)
            cell.track_items = cell.track_items[-2:]
        Ctx.prev_cell_needs_checking = False
        return

    def get_cell_index(i: int = 0, j: int = 0) -> int:
        return int(j) * Field.cells_y + int(i)


class TrackItem:
    name_direction_map = {
        "s0": [Direction.RIGHT, Direction.LEFT],
        "c0": [Direction.LEFT, Direction.DOWN],
        "s90": [Direction.UP, Direction.DOWN],
        "c90": [Direction.RIGHT, Direction.DOWN],
        "c180": [Direction.RIGHT, Direction.UP],
        "c270": [Direction.UP, Direction.LEFT],
    }

    def __init__(self, resource_name: str):
        self.surface = Resources.track_surfaces[resource_name]
        self.directions = TrackItem.name_direction_map[resource_name]

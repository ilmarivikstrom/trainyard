import pygame as pg

from src.config import Config
from src.direction import Direction
from src.game_context import Ctx, Resources
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")

class Cell(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, color: pg.Color):
        super().__init__()
        self.i = i
        self.j = j
        self.image = Resources.img_surfaces["bg_tile"]
        self.rect = self.image.get_rect()
        self.rect.x = i * Config.cell_size + Config.padding_x
        self.rect.y = j * Config.cell_size + Config.padding_y

        self.mouse_on = False
        self.tracks = []

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
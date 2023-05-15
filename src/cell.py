import pygame as pg

from src.config import Config
from src.direction import Direction
from src.game_state import State
from src.resources import Resources
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)

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


    def flip_tracks(self):
        if len(self.tracks) > 1:
            for track in self.tracks:
                track.toggle_bright()
            self.tracks.reverse()
            pg.mixer.music.load("res/click.wav")
            pg.mixer.music.set_volume(0.2)
            pg.mixer.music.play()


    def check_mouse_collision(self):
        if self.rect.collidepoint(State.mouse_pos):
            if not self.mouse_on:
                #logger.debug(f"Mouse entered Cell at {(self.i, self.j)}")
                handle_mouse_cell_enter(self)
            self.mouse_on = True
        else:
            self.mouse_on = False


def handle_mouse_cell_enter(cell) -> None:
    previous_cell = State.curr_cell
    State.prev_cell_needs_checking = True
    State.prev_cell = previous_cell
    State.curr_cell = pg.Vector2(cell.i, cell.j)
    State.prev_movement = State.curr_movement

    if (
        State.prev_cell is None
        or State.prev_cell.x is None
        or State.prev_cell.y is None
    ):
        logger.warning("Previous mouse cell was None. Returning from mouse handling.")
        return
    if (State.curr_cell.x - State.prev_cell.x == 1) and (
        State.curr_cell.y == State.prev_cell.y
    ):
        State.curr_movement = Direction.RIGHT
    elif (
        State.curr_cell.x - State.prev_cell.x == -1
    ) and (State.curr_cell.y == State.prev_cell.y):
        State.curr_movement = Direction.LEFT
    elif (State.curr_cell.x == State.prev_cell.x) and (
        State.curr_cell.y - State.prev_cell.y == 1
    ):
        State.curr_movement = Direction.DOWN
    elif (State.curr_cell.x == State.prev_cell.x) and (
        State.curr_cell.y - State.prev_cell.y == -1
    ):
        State.curr_movement = Direction.UP
    else:
        State.curr_movement = None
        logger.info(
            f"Mouse warped. Prev: ({State.prev_cell.x}, {State.prev_cell.y}), current: ({State.curr_cell.x}, {State.curr_cell.y})"
        )

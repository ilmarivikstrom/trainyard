import pygame as pg

from src.config import Config

from src.field import Field
from src.game_state import State, Phase
from src.phases import exit_phase, gameplay_phase, main_menu_phase
from src.resources import Resources
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")


def main() -> None:
    initial_setup()
    clock = pg.time.Clock()

    while True:
        if State.game_phase == Phase.MAIN_MENU:
            main_menu_phase()
        elif State.game_phase == Phase.GAME_END:
            exit_phase()
        elif State.game_phase == Phase.GAMEPLAY:
            gameplay_phase()
        pg.display.update()
        clock.tick(Config.FPS)


def initial_setup():
    pg.init()
    pg.display.set_caption("trainyard")
    width = Config.padding_x + Config.cells_x * Config.cell_size + Config.padding_x
    height = (
        Config.padding_y
        + Config.cells_y * Config.cell_size
        + Config.padding_y
        + Config.padding_y
    )
    State.screen_surface = pg.display.set_mode((width, height))
    Resources.load_resources()
    Field.initialize_grid()


if __name__ == "__main__":
    main()

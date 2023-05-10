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
        State.current_tick += 1
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
    width = Config.screen_width
    height = Config.screen_height
    State.screen_surface = pg.display.set_mode((width, height))
    Resources.load_resources()
    Field.initialize_grid()


if __name__ == "__main__":
    main()

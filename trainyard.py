import pygame as pg

from src.config import Config
from src.field import Field
from src.game_state import Phase, State
from src.phases import exit_phase, gameplay_phase, main_menu_phase
from src.resources import Resources
from src.sound import Sound
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


def main() -> None:
    initial_setup()
    field = initialize_level()
    clock = pg.time.Clock()

    Sound.start_music()

    while True:
        State.current_tick += 1
        if State.game_phase == Phase.MAIN_MENU:
            main_menu_phase(field)
        elif State.game_phase == Phase.GAME_END:
            exit_phase()
        elif State.game_phase == Phase.GAMEPLAY:
            gameplay_phase(field)
        pg.display.update()
        clock.tick(Config.FPS)


def initial_setup():
    pg.display.set_caption("trainyard")
    Resources.load_resources()


def initialize_level() -> Field:
    field = Field()
    field.initialize_grid()
    # TODO: Instead of the following, load a level from somewhere and place the object accordingly.
    field.add_level_objects()
    return field


if __name__ == "__main__":
    main()

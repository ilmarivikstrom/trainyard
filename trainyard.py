import pygame as pg

from src.config import Config
from src.field import Field
from src.game_state import Phase, State
from src.phases import exit_phase, gameplay_phase, main_menu_phase
from src.graphics import Graphics
from src.screen import Screen
from src.sound import Sound
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


def main() -> None:
    screen = Screen()
    initial_pygame_setup()
    state = State()
    field = Field()
    field.initialize_grid()
    clock = pg.time.Clock()

    if Config.play_music:
        Sound.play_music()

    while True:
        state.global_status.current_tick += 1
        if state.game_phase == Phase.MAIN_MENU:
            main_menu_phase(state, screen, field)
        elif state.game_phase == Phase.GAME_END:
            exit_phase()
        elif state.game_phase == Phase.GAMEPLAY:
            gameplay_phase(state, screen, field)
        pg.display.update()
        clock.tick(Config.FPS)


def initial_pygame_setup():
    pg.display.set_caption("trainyard")
    Graphics.load_resources()



if __name__ == "__main__":
    main()

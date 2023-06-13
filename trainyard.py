import pygame as pg

from src.config import Config
from src.field import Field
from src.graphics import Graphics
from src.phase_exit import exit_phase
from src.phase_gameplay import gameplay_phase
#from src.phase_mainmenu import mainmenu_phase
from src.screen import Screen
from src.sound import Sound
from src.state import Phase, State
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


def initial_pygame_setup():
    pg.display.set_caption("trainyard")
    Graphics.load_resources()


def main() -> None:
    screen = Screen()
    initial_pygame_setup()
    state = State()
    field = Field(level=0)
    field.initialize_grid()
    clock = pg.time.Clock()

    Sound.init_music(song_name="Song 9")

    if Config.play_music:
        Sound.play_music()

    while True:
        if state.game_phase == Phase.MAIN_MENU:
            #mainmenu_phase(state, screen)
            gameplay_phase(state, screen, field)
        elif state.game_phase == Phase.EXIT:
            exit_phase()
        elif state.game_phase == Phase.GAMEPLAY:
            gameplay_phase(state, screen, field)

        state.global_status.current_tick += 1
        pg.display.update()
        clock.tick(Config.FPS)


if __name__ == "__main__":
    main()

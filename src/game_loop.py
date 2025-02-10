"""Game loop."""

import pygame as pg

from src.config import Config
from src.field import Field
from src.graphics import Graphics
from src.phase_exit import exit_phase
from src.phase_gameplay import gameplay_phase
from src.screen import Screen
from src.sound import Sound
from src.state import Phase, State
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class GameLoop:
    def __init__(self) -> None:
        self.screen = Screen()
        pg.display.set_caption("locomotive")
        Graphics.load_resources()
        self.state = State()
        self.field = Field(level=0)
        self.field.initialize_grid()
        self.clock = pg.time.Clock()

        Sound.init_music(song_name="Song 9")

    def loop(self) -> None:
        if Config.play_music:
            Sound.play_music()
        while True:
            if self.state.game_phase == Phase.MAIN_MENU:
                gameplay_phase(self.state, self.screen, self.field)
            elif self.state.game_phase == Phase.EXIT:
                exit_phase()
            elif self.state.game_phase == Phase.GAMEPLAY:
                gameplay_phase(self.state, self.screen, self.field)

            self.state.global_status.current_tick += 1
            pg.display.update()
            self.clock.tick(Config.FPS)

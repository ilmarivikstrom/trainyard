from dataclasses import dataclass
from enum import Enum

import pygame as pg

from src.config import Config
from src.profiling import Profiler
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)

class Phase(Enum):
    MAIN_MENU = 0
    GAMEPLAY = 1
    GAME_END = 2


@dataclass
class GlobalStatus:
    current_tick: int = 0


@dataclass
class GameplayStatus:
    trains_crashed: int = 0
    trains_released: bool = False
    delete_mode: bool = False
    prev_cell_needs_checking: bool = False
    current_level_passed = False
    background_location: tuple[float, float] = (0.0, 0.0)


class State:
    def __init__(self):
        self.game_phase = Phase.MAIN_MENU
        self.screen_surface = pg.display.set_mode((Config.screen_width, Config.screen_height))
        self.global_status = GlobalStatus()
        self.gameplay = GameplayStatus()
        self.profiler: Profiler = Profiler()

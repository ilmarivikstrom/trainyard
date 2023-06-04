from dataclasses import dataclass
from enum import Enum
from typing import Tuple

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


class GameplayStatus:
    def __init__(self):
        self.trains_crashed: int = 0
        self.trains_released: bool = False
        self.delete_mode: bool = False
        self.prev_cell_needs_checking: bool = False
        self.current_level_passed = False
        self.background_location: Tuple[float, float] = (0.0, 0.0)


    def reset(self):
        self.trains_crashed = 0
        self.trains_released = False
        self.current_level_passed = False


class State:
    def __init__(self):
        self.game_phase: Phase = Phase.MAIN_MENU
        self.global_status: GlobalStatus = GlobalStatus()
        self.gameplay: GameplayStatus = GameplayStatus()
        self.profiler: Profiler = Profiler()

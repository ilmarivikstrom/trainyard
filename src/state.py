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
    EXIT = 2


@dataclass
class GlobalStatus:
    current_tick: int = 0


@dataclass
class GameplayStatus:
    in_delete_mode: bool = False
    current_level_passed = False
    background_location: Tuple[float, float] = (0.0, 0.0)


@dataclass
class MainMenuStatus:
    something: str = "something"


class State:
    def __init__(self):
        self.profiler: Profiler = Profiler()
        self.global_status: GlobalStatus = GlobalStatus()
        self.gameplay: GameplayStatus = GameplayStatus()
        self.mainmenu: MainMenuStatus = MainMenuStatus()
        self.game_phase: Phase = Phase.GAMEPLAY

    def reset_gameplay_status(self) -> None:
        self.gameplay.current_level_passed = False

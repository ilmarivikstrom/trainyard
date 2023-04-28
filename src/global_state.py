from enum import Enum


class GameStatus(Enum):
    MAIN_MENU = 0
    GAMEPLAY = 1
    GAME_END = 2


class GlobalState:
    game_status = GameStatus.MAIN_MENU
    screen_surface = None

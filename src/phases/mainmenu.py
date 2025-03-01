"""Phase: Main menu."""

import pygame as pg
from pygame.locals import KEYDOWN, QUIT

from src.color_constants import GRAY10
from src.config import Config
from src.screen import Screen
from src.state import Phase, State
from src.user.control import UserControl
from src.utils.utils import setup_logging

logger = setup_logging(log_level=Config.LOG_LEVEL)


def mainmenu_phase(state: State, screen: Screen) -> None:
    UserControl.update_user_events()
    screen.surface.fill(GRAY10)
    check_for_pg_mainmenu_events(state)
    check_for_gameplay_command(state)
    check_for_exit_command(state)


def check_for_pg_mainmenu_events(state: State) -> None:
    for event in pg.event.get():
        if event.type == QUIT:
            state.game_phase = Phase.EXIT
            logger.info(f"Moving to phase {state.game_phase}")


def check_for_exit_command(state: State) -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == UserControl.EXIT:
            state.game_phase = Phase.EXIT
            logger.info(f"Moving to phase {state.game_phase}")


def check_for_gameplay_command(state: State) -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == UserControl.GAMEPLAY:
            state.game_phase = Phase.GAMEPLAY
            logger.info(f"Moving to phase {state.game_phase}")

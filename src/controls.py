import logging
import pygame
from pygame.locals import QUIT
from .global_state import GameStatus, GlobalState


class UserControl:
    MAIN_MENU = pygame.K_ESCAPE
    EXIT = pygame.K_q
    GAMEPLAY = pygame.K_RETURN
    MOUSE_DOWN = pygame.MOUSEBUTTONDOWN


def check_quit_event(logger: logging.Logger) -> None:
    for event in pygame.event.get():
        if event.type == QUIT:
            GlobalState.game_status = GameStatus.GAME_END
            logger.info(f"Moving to state {GlobalState.game_status}")

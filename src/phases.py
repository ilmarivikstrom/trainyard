import logging
import sys
import pygame
from pygame.locals import QUIT
from src.controls import UserControl, check_quit_event
from src.global_state import GameStatus, GlobalState
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")


def main_menu_phase():
    GlobalState.screen_surface.fill((0, 255, 255))
    check_quit_event(logger)
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[UserControl.GAMEPLAY]:
        GlobalState.game_status = GameStatus.GAMEPLAY
        logger.info(f"Moving to state {GlobalState.game_status}")
    elif pressed_keys[UserControl.EXIT]:
        GlobalState.game_status = GameStatus.GAME_END
        logger.info(f"Moving to state {GlobalState.game_status}")


def gameplay_phase():
    GlobalState.screen_surface.fill((255, 0, 255))
    pygame.draw.circle(
        GlobalState.screen_surface,
        color=pygame.Color(100, 100, 100),
        center=(200, 200),
        radius=10,
    )
    check_quit_event(logger)
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[UserControl.MAIN_MENU]:
        GlobalState.game_status = GameStatus.MAIN_MENU
        logger.info(f"Moving to state {GlobalState.game_status}")


def exit_phase():
    logger.info("Exiting game...")
    pygame.quit()
    sys.exit()

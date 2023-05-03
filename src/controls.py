import pygame as pg

from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")


class UserControl:
    MAIN_MENU = pg.K_ESCAPE
    EXIT = pg.K_q
    GAMEPLAY = pg.K_RETURN
    MOUSE_DOWN = pg.MOUSEBUTTONDOWN
    DELETE_MODE = pg.K_LSHIFT


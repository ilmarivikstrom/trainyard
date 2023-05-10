import pygame as pg

from src.config import Config
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class UserControl:
    MAIN_MENU = pg.K_ESCAPE
    EXIT = pg.K_q
    GAMEPLAY = pg.K_RETURN
    MOUSE_DOWN = pg.MOUSEBUTTONDOWN
    DELETE_MODE = pg.K_LSHIFT

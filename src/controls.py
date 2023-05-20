import pygame as pg

from src.config import Config
from src.direction import Direction
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class UserControl:
    MAIN_MENU = pg.K_ESCAPE
    EXIT = pg.K_q
    GAMEPLAY = pg.K_RETURN
    MOUSE_DOWN = pg.MOUSEBUTTONDOWN
    DELETE_MODE = pg.K_LSHIFT

    mouse_pos = pg.Vector2(-1, -1)
    mouse_pressed = (False, False, False)
    curr_cell = pg.Vector2(-1, -1)
    prev_cell = pg.Vector2(-1, -1)

    pressed_keys: pg.key.ScancodeWrapper = pg.key.ScancodeWrapper()

    spacebar_down = False
    wait_for_space_up = False

    curr_movement = Direction.NONE
    prev_movement = Direction.NONE

    delete_mode = False


    @staticmethod
    def update_user_controls():
        UserControl.mouse_pos = pg.mouse.get_pos()
        UserControl.pressed_keys = pg.key.get_pressed()
        UserControl.mouse_pressed = pg.mouse.get_pressed()
        if not UserControl.mouse_pressed[0]:
            UserControl.curr_movement = None
            UserControl.prev_movement = None
            UserControl.prev_cell = None
        if UserControl.pressed_keys[UserControl.DELETE_MODE]:
            UserControl.delete_mode = True
        else:
            UserControl.delete_mode = False
        if UserControl.pressed_keys[pg.K_1]:
            Config.FPS = Config.FPS_list[0]
        elif UserControl.pressed_keys[pg.K_2]:
            Config.FPS = Config.FPS_list[1]
        elif UserControl.pressed_keys[pg.K_3]:
            Config.FPS = Config.FPS_list[2]
        elif UserControl.pressed_keys[pg.K_4]:
            Config.FPS = Config.FPS_list[3]
        elif UserControl.pressed_keys[pg.K_5]:
            Config.FPS = Config.FPS_list[4]
        elif UserControl.pressed_keys[pg.K_6]:
            Config.FPS = Config.FPS_list[5]
        elif UserControl.pressed_keys[pg.K_7]:
            Config.FPS = Config.FPS_list[6]
        elif UserControl.pressed_keys[pg.K_8]:
            Config.FPS = Config.FPS_list[7]
        elif UserControl.pressed_keys[pg.K_9]:
            Config.FPS = Config.FPS_list[8]

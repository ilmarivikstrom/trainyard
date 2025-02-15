"""User control."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import pygame as pg
from pygame import (
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_6,
    K_7,
    K_ESCAPE,
    K_LSHIFT,
    K_RETURN,
    K_RSHIFT,
    MOUSEBUTTONDOWN,
    K_q,
    K_s,
)

from src.config import Config
from src.coordinate import Coordinate
from src.direction import Direction
from src.utils import setup_logging

if TYPE_CHECKING:
    from pygame.event import Event

logger = setup_logging(log_level=Config.log_level)


class UserControl:
    MAIN_MENU = K_ESCAPE
    EXIT = K_q
    GAMEPLAY = K_RETURN
    MOUSE_DOWN = MOUSEBUTTONDOWN
    DELETE_MODE_1 = K_LSHIFT
    DELETE_MODE_2 = K_RSHIFT
    SAVE_GAME = K_s

    mouse_pos = Coordinate(-1, -1)
    mouse_pressed: tuple[bool, bool, bool] = (False, False, False)
    curr_cell: Coordinate = Coordinate(-1, -1)
    prev_cell: Coordinate | None = None

    mouse_entered_new_cell: bool = False

    pressed_keys: pg.key.ScancodeWrapper = pg.key.ScancodeWrapper()

    spacebar_down: bool = False
    wait_for_space_up: bool = False

    curr_movement: Direction = Direction.NONE
    prev_movement: Direction = Direction.NONE

    events: ClassVar[list[Event]] = []

    @staticmethod
    def update_user_events() -> None:
        UserControl.events = []
        for event in pg.event.get():
            UserControl.events.append(event)

        UserControl.mouse_pos = Coordinate.from_tuple(pg.mouse.get_pos())
        UserControl.pressed_keys = pg.key.get_pressed()
        UserControl.mouse_pressed = pg.mouse.get_pressed()

        if not UserControl.mouse_pressed[0]:
            UserControl.curr_movement = Direction.NONE
            UserControl.prev_movement = Direction.NONE
            UserControl.prev_cell = None
        if UserControl.pressed_keys[K_1]:
            Config.FPS = Config.FPS_list[0]
        elif UserControl.pressed_keys[K_2]:
            Config.FPS = Config.FPS_list[1]
        elif UserControl.pressed_keys[K_3]:
            Config.FPS = Config.FPS_list[2]
        elif UserControl.pressed_keys[K_4]:
            Config.FPS = Config.FPS_list[3]
        elif UserControl.pressed_keys[K_5]:
            Config.FPS = Config.FPS_list[4]
        elif UserControl.pressed_keys[K_6]:
            Config.FPS = Config.FPS_list[5]
        elif UserControl.pressed_keys[K_7]:
            Config.FPS = Config.FPS_list[6]

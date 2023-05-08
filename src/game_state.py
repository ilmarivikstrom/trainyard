from enum import Enum

import pygame as pg

from src.config import Config
from src.controls import UserControl
from src.direction import Direction


class Phase(Enum):
    MAIN_MENU = 0
    GAMEPLAY = 1
    GAME_END = 2


class State:
    game_phase = Phase.MAIN_MENU
    screen_surface = None
    resources = None

    mouse_pos = pg.Vector2(-1, -1)
    mouse_pressed = (False, False, False)
    pressed_keys = []

    curr_cell = pg.Vector2(-1, -1)
    prev_cell = pg.Vector2(-1, -1)
    prev_cell_needs_checking = False
    curr_movement = Direction.NONE
    prev_movement = Direction.NONE

    trains = []
    cell_sprites = pg.sprite.Group()
    train_sprites = pg.sprite.Group()
    angular_vel = 0.03125

    spacebar_down = False
    train_go = False
    wait_for_space_up = False

    departure_station = None
    arrival_station = None
    station_sprites = pg.sprite.Group()

    @staticmethod
    def update_gameplay_state() -> None:
        State.mouse_pos = pg.mouse.get_pos()
        State.pressed_keys = pg.key.get_pressed()
        State.mouse_pressed = pg.mouse.get_pressed()
        if State.mouse_pressed[0] is False:
            State.prev_movement = None
            State.curr_movement = None
            State.prev_cell = None
        if State.pressed_keys[UserControl.DELETE_MODE]:
            State.delete_mode = True
        else:
            State.delete_mode = False
        if State.pressed_keys[pg.K_1]:
            Config.FPS = Config.FPS_list[0]
        elif State.pressed_keys[pg.K_2]:
            Config.FPS = Config.FPS_list[1]
        elif State.pressed_keys[pg.K_3]:
            Config.FPS = Config.FPS_list[2]
        elif State.pressed_keys[pg.K_4]:
            Config.FPS = Config.FPS_list[3]
        elif State.pressed_keys[pg.K_5]:
            Config.FPS = Config.FPS_list[4]
        elif State.pressed_keys[pg.K_6]:
            Config.FPS = Config.FPS_list[5]
        elif State.pressed_keys[pg.K_7]:
            Config.FPS = Config.FPS_list[6]
        elif State.pressed_keys[pg.K_8]:
            Config.FPS = Config.FPS_list[7]
        elif State.pressed_keys[pg.K_9]:
            Config.FPS = Config.FPS_list[8]

        if State.pressed_keys[pg.K_SPACE] and not State.wait_for_space_up:
            State.train_go = not State.train_go
            State.wait_for_space_up = True
            print("Space down.")
        if State.wait_for_space_up:
            if not State.pressed_keys[pg.K_SPACE]:
                State.wait_for_space_up = False
                print("Space released.")

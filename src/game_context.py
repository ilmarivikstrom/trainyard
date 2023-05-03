from typing import List
import pygame as pg
from enum import Enum
from src.controls import UserControl


class Phase(Enum):
    MAIN_MENU = 0
    GAMEPLAY = 1
    GAME_END = 2


class Direction(Enum):
    NONE = -1
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3
    RIGHTUP = 4
    UPLEFT = 5
    LEFTDOWN = 6
    RIGHTDOWN = 7


class Resources:
    img_surfaces = {}
    track_surfaces = {}
    train_surfaces = {}

    def load_resources() -> List[pg.Surface]:
        Resources.img_surfaces = {
            "track_s": pg.image.load("res/s0.png").convert_alpha(),
            "track_c": pg.image.load("res/c0.png").convert_alpha(),
            "train": pg.image.load("res/train0.png").convert_alpha(),
        }
        Resources.track_surfaces = {
            "s0": pg.transform.rotate(Resources.img_surfaces["track_s"], 0),
            "s90": pg.transform.rotate(Resources.img_surfaces["track_s"], 90),
            "c0": pg.transform.rotate(Resources.img_surfaces["track_c"], 0),
            "c90": pg.transform.rotate(Resources.img_surfaces["track_c"], 90),
            "c180": pg.transform.rotate(Resources.img_surfaces["track_c"], 180),
            "c270": pg.transform.rotate(Resources.img_surfaces["track_c"], 270),
        }
        Resources.train_surfaces = {
            "train0": pg.transform.rotate(Resources.img_surfaces["train"], 0),
            "train90": pg.transform.rotate(Resources.img_surfaces["train"], 90),
            "train180": pg.transform.rotate(Resources.img_surfaces["train"], 180),
            "train270": pg.transform.rotate(Resources.img_surfaces["train"], 270),
        }


class Ctx:
    game_phase = Phase.MAIN_MENU
    screen_surface = None
    resources = None

    mouse_pos = pg.Vector2(-1, -1)
    mouse_pressed = (False, False, False)
    pressed_keys = []

    delete_mode = False

    curr_cell = pg.Vector2(-1, -1)
    prev_cell = pg.Vector2(-1, -1)
    prev_cell_needs_checking = False
    curr_movement = Direction.NONE
    prev_movement = Direction.NONE

    train_pos = pg.Vector2(128, 128)
    train_vel = pg.Vector2(0, 0)
    train_dir = Direction.RIGHT

    train_on_track = False



    def update_gameplay_state():
        Ctx.mouse_pos = pg.mouse.get_pos()
        Ctx.pressed_keys = pg.key.get_pressed()
        Ctx.mouse_pressed = pg.mouse.get_pressed()
        if Ctx.mouse_pressed[0] is False:
            Ctx.prev_movement = None
            Ctx.curr_movement = None
            Ctx.prev_cell = None
        if Ctx.pressed_keys[UserControl.DELETE_MODE]:
            Ctx.delete_mode = True
        else:
            Ctx.delete_mode = False


    def update_trains():
        Ctx.train_pos.x = round(Ctx.train_pos.x + Ctx.train_vel.x)
        Ctx.train_pos.y = round(Ctx.train_pos.y + Ctx.train_vel.y)
        print(Ctx.train_pos)

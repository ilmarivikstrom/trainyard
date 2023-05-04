from enum import Enum
from typing import List

import pygame as pg

from src.config import Config
from src.controls import UserControl
from src.direction import Direction


class Phase(Enum):
    MAIN_MENU = 0
    GAMEPLAY = 1
    GAME_END = 2


class Resources:
    img_surfaces = {}
    track_surfaces = {}
    train_surfaces = {}

    def load_resources() -> List[pg.Surface]:
        Resources.img_surfaces = {
            "train": pg.image.load("res/train1.png").convert_alpha(),
            "bg_tile": pg.image.load("res/bg_tile.png").convert_alpha(),
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

    train = None
    angle = 0
    cell_sprites = pg.sprite.Group()
    train_sprites = pg.sprite.Group()

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
        if Ctx.pressed_keys[pg.K_s]:
            Config.FPS = 5
        else:
            Config.FPS = Config.orig_FPS

    def update_trains():
        if not Ctx.train.on_track:
            Ctx.train.velocity.x = 0
            Ctx.train.velocity.y = 0
        Ctx.train.pos.x = Ctx.train.pos.x + Ctx.train.velocity.x
        Ctx.train.pos.y = Ctx.train.pos.y + Ctx.train.velocity.y
        Ctx.train.rect.x = Ctx.train.pos.x
        Ctx.train.rect.y = Ctx.train.pos.y

from typing import List

import pygame as pg


class Resources:
    img_surfaces = {}
    track_surfaces = {}
    train_surfaces = {}

    @staticmethod
    def load_resources() -> List[pg.Surface]:
        Resources.img_surfaces = {
            "gradient": pg.image.load("res/gradient.png").convert_alpha(),
            "train_red": pg.image.load("res/train_red.png").convert_alpha(),
            "train_blue": pg.image.load("res/train_blue.png").convert_alpha(),
            "train_yellow": pg.image.load("res/train_yellow.png").convert_alpha(),
            "bg_tile": pg.image.load("res/bg_tile.png").convert_alpha(),
            "track_s_bright": pg.image.load("res/track_s_bright.png").convert_alpha(),
            "track_c_bright": pg.image.load("res/track_c_bright.png").convert_alpha(),
            "track_s_dark": pg.image.load("res/track_s_dark.png").convert_alpha(),
            "track_c_dark": pg.image.load("res/track_c_dark.png").convert_alpha(),
            "departure": pg.image.load("res/departure_station.png").convert_alpha(),
            "arrival": pg.image.load("res/arrival_station.png").convert_alpha(),
            "blue_train_1": pg.image.load("res/blue_train_1.png").convert_alpha(),
            "blue_train_2": pg.image.load("res/blue_train_2.png").convert_alpha(),
            "blue_train_3": pg.image.load("res/blue_train_3.png").convert_alpha(),
            "blue_train_4": pg.image.load("res/blue_train_4.png").convert_alpha()
        }

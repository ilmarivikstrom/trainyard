from typing import List
import pygame as pg

class Resources:
    img_surfaces = {}
    track_surfaces = {}
    train_surfaces = {}

    @staticmethod
    def load_resources() -> List[pg.Surface]:
        Resources.img_surfaces = {
            "train": pg.image.load("res/train_green.png").convert_alpha(),
            "bg_tile": pg.image.load("res/bg_tile.png").convert_alpha(),
            "track_s_bright": pg.image.load("res/track_s_bright.png").convert_alpha(),
            "track_c_bright": pg.image.load("res/track_c_bright.png").convert_alpha(),
            "track_s_dark": pg.image.load("res/track_s_dark.png").convert_alpha(),
            "track_c_dark": pg.image.load("res/track_c_dark.png").convert_alpha(),
            "departure": pg.image.load("res/departure_station.png").convert_alpha(),
            "arrival": pg.image.load("res/arrival_station.png").convert_alpha()
        }

from typing import List
import pygame as pg

class Resources:
    img_surfaces = {}
    track_surfaces = {}
    train_surfaces = {}

    @staticmethod
    def load_resources() -> List[pg.Surface]:
        Resources.img_surfaces = {
            "train": pg.image.load("res/train1.png").convert_alpha(),
            "bg_tile": pg.image.load("res/bg_tile.png").convert_alpha(),
            "departure": pg.image.load("res/departure_station.png").convert_alpha(),
            "arrival": pg.image.load("res/arrival_station.png").convert_alpha()
        }

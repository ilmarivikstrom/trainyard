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
        }
        Resources.train_surfaces = {
            "train0": pg.transform.rotate(Resources.img_surfaces["train"], 0),
            "train90": pg.transform.rotate(Resources.img_surfaces["train"], 90),
            "train180": pg.transform.rotate(Resources.img_surfaces["train"], 180),
            "train270": pg.transform.rotate(Resources.img_surfaces["train"], 270),
        }

from typing import List

import pygame as pg


class Resources:
    img_surfaces = {}

    @staticmethod
    def load_resources() -> None:
        Resources.img_surfaces = {
            "day_cycle": pg.image.load("res/scrolling_day_cycle.png").convert_alpha(),
            "gradient": pg.image.load("res/gradient.png").convert_alpha(),
            "train_red": pg.image.load("res/train_red.png").convert_alpha(),
            "train_blue": pg.image.load("res/train_blue.png").convert_alpha(),
            "train_yellow": pg.image.load("res/train_yellow.png").convert_alpha(),
            "train_orange": pg.image.load("res/train_orange.png").convert_alpha(),
            "train_green": pg.image.load("res/train_green.png").convert_alpha(),
            "train_purple": pg.image.load("res/train_purple.png").convert_alpha(),
            "bg_tile": pg.image.load("res/bg_tile.png").convert_alpha(),
            "track_s_bright": pg.image.load("res/track_s_bright.png").convert_alpha(),
            "track_c_bright": pg.image.load("res/track_c_bright.png").convert_alpha(),
            "track_s_dark": pg.image.load("res/track_s_dark.png").convert_alpha(),
            "track_c_dark": pg.image.load("res/track_c_dark.png").convert_alpha(),
            "departure": pg.image.load("res/departure_station.png").convert_alpha(),
            "arrival": pg.image.load("res/arrival_station.png").convert_alpha(),
            "blue_goal_1": pg.image.load("res/goal_blue.png").convert_alpha(),
            "blue_goal_2": pg.transform.rotate(pg.image.load("res/goal_blue.png").convert_alpha(), -90),
            "blue_goal_3": pg.transform.rotate(pg.image.load("res/goal_blue.png").convert_alpha(), 90),
            "blue_goal_4": pg.transform.rotate(pg.image.load("res/goal_blue.png").convert_alpha(), 180),
            "red_goal_1": pg.image.load("res/goal_red.png").convert_alpha(),
            "red_goal_2": pg.transform.rotate(pg.image.load("res/goal_red.png").convert_alpha(), -90),
            "red_goal_3": pg.transform.rotate(pg.image.load("res/goal_red.png").convert_alpha(), 90),
            "red_goal_4": pg.transform.rotate(pg.image.load("res/goal_red.png").convert_alpha(), 180),
            "yellow_goal_1": pg.image.load("res/goal_yellow.png").convert_alpha(),
            "yellow_goal_2": pg.transform.rotate(pg.image.load("res/goal_yellow.png").convert_alpha(), -90),
            "yellow_goal_3": pg.transform.rotate(pg.image.load("res/goal_yellow.png").convert_alpha(), 90),
            "yellow_goal_4": pg.transform.rotate(pg.image.load("res/goal_yellow.png").convert_alpha(), 180),
            "orange_goal_1": pg.image.load("res/goal_orange.png").convert_alpha(),
            "orange_goal_2": pg.transform.rotate(pg.image.load("res/goal_orange.png").convert_alpha(), -90),
            "orange_goal_3": pg.transform.rotate(pg.image.load("res/goal_orange.png").convert_alpha(), 90),
            "orange_goal_4": pg.transform.rotate(pg.image.load("res/goal_orange.png").convert_alpha(), 180),
            "green_goal_1": pg.image.load("res/goal_green.png").convert_alpha(),
            "green_goal_2": pg.transform.rotate(pg.image.load("res/goal_green.png").convert_alpha(), -90),
            "green_goal_3": pg.transform.rotate(pg.image.load("res/goal_green.png").convert_alpha(), 90),
            "green_goal_4": pg.transform.rotate(pg.image.load("res/goal_green.png").convert_alpha(), 180),
            "purple_goal_1": pg.image.load("res/goal_purple.png").convert_alpha(),
            "purple_goal_2": pg.transform.rotate(pg.image.load("res/goal_purple.png").convert_alpha(), -90),
            "purple_goal_3": pg.transform.rotate(pg.image.load("res/goal_purple.png").convert_alpha(), 90),
            "purple_goal_4": pg.transform.rotate(pg.image.load("res/goal_purple.png").convert_alpha(), 180),
        }

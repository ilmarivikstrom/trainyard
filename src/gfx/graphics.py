"""Graphics."""

from typing import ClassVar

import pygame as pg


class Graphics:
    img_surfaces: ClassVar[dict[str, pg.Surface]] = {}

    @staticmethod
    def load_resources() -> None:
        Graphics.img_surfaces = {
            "shift_key": pg.image.load("assets/sprites/shift.png").convert_alpha(),
            "checkmark": pg.image.load("assets/sprites/checkmark.png").convert_alpha(),
            "train_red": pg.image.load("assets/sprites/train_red.png").convert_alpha(),
            "train_blue": pg.image.load(
                "assets/sprites/train_blue.png",
            ).convert_alpha(),
            "train_yellow": pg.image.load(
                "assets/sprites/train_yellow.png",
            ).convert_alpha(),
            "train_orange": pg.image.load(
                "assets/sprites/train_orange.png",
            ).convert_alpha(),
            "train_green": pg.image.load(
                "assets/sprites/train_green.png",
            ).convert_alpha(),
            "train_purple": pg.image.load(
                "assets/sprites/train_purple.png",
            ).convert_alpha(),
            "train_brown": pg.image.load(
                "assets/sprites/train_brown.png",
            ).convert_alpha(),
            "bg_tile": pg.image.load("assets/sprites/bg_tile.png").convert_alpha(),
            "rock": pg.image.load("assets/sprites/rock.png").convert_alpha(),
            "track_s_bright": pg.image.load(
                "assets/sprites/track_s_bright.png",
            ).convert_alpha(),
            "track_c_bright": pg.image.load(
                "assets/sprites/track_c_bright.png",
            ).convert_alpha(),
            "track_s_dark": pg.image.load(
                "assets/sprites/track_s_dark.png",
            ).convert_alpha(),
            "track_c_dark": pg.image.load(
                "assets/sprites/track_c_dark.png",
            ).convert_alpha(),
            "departure": pg.image.load(
                "assets/sprites/departure_station.png",
            ).convert_alpha(),
            "arrival": pg.image.load(
                "assets/sprites/arrival_station.png",
            ).convert_alpha(),
            "blue_goal_1": pg.image.load(
                "assets/sprites/goal_blue.png",
            ).convert_alpha(),
            "painter": pg.image.load("assets/sprites/painter.png").convert_alpha(),
            "splitter": pg.image.load("assets/sprites/splitter.png").convert_alpha(),
            "blue_goal_2": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_blue.png").convert_alpha(),
                -90,
            ),
            "blue_goal_3": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_blue.png").convert_alpha(),
                90,
            ),
            "blue_goal_4": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_blue.png").convert_alpha(),
                180,
            ),
            "red_goal_1": pg.image.load("assets/sprites/goal_red.png").convert_alpha(),
            "red_goal_2": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_red.png").convert_alpha(),
                -90,
            ),
            "red_goal_3": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_red.png").convert_alpha(),
                90,
            ),
            "red_goal_4": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_red.png").convert_alpha(),
                180,
            ),
            "yellow_goal_1": pg.image.load(
                "assets/sprites/goal_yellow.png",
            ).convert_alpha(),
            "yellow_goal_2": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_yellow.png").convert_alpha(),
                -90,
            ),
            "yellow_goal_3": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_yellow.png").convert_alpha(),
                90,
            ),
            "yellow_goal_4": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_yellow.png").convert_alpha(),
                180,
            ),
            "orange_goal_1": pg.image.load(
                "assets/sprites/goal_orange.png",
            ).convert_alpha(),
            "orange_goal_2": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_orange.png").convert_alpha(),
                -90,
            ),
            "orange_goal_3": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_orange.png").convert_alpha(),
                90,
            ),
            "orange_goal_4": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_orange.png").convert_alpha(),
                180,
            ),
            "green_goal_1": pg.image.load(
                "assets/sprites/goal_green.png",
            ).convert_alpha(),
            "green_goal_2": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_green.png").convert_alpha(),
                -90,
            ),
            "green_goal_3": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_green.png").convert_alpha(),
                90,
            ),
            "green_goal_4": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_green.png").convert_alpha(),
                180,
            ),
            "purple_goal_1": pg.image.load(
                "assets/sprites/goal_purple.png",
            ).convert_alpha(),
            "purple_goal_2": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_purple.png").convert_alpha(),
                -90,
            ),
            "purple_goal_3": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_purple.png").convert_alpha(),
                90,
            ),
            "purple_goal_4": pg.transform.rotate(
                pg.image.load("assets/sprites/goal_purple.png").convert_alpha(),
                180,
            ),
        }

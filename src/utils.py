import logging
from typing import List

import pygame as pg


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    fmt = "%(asctime)s %(funcName)20s(): %(message)s"
    logging.basicConfig(level=log_level, format=fmt)
    return logging.getLogger()


def get_background_color_array() -> List[pg.Color]:
    color_array: List[pg.Color] = []
    with open("assets/sprites/day_night_array.csv", mode="r", encoding="utf-8") as array_file:
        for line in array_file.readlines():
            line_stripped = line.strip()
            tuple_items = line_stripped.split(",")
            color_tuple = (int(tuple_items[0]), int(tuple_items[1]), int(tuple_items[2]), int(tuple_items[3]))
            color = pg.Color(color_tuple)
            color_array.append(color)
    return color_array


def rot_center(original_image, angle_degrees: float) -> pg.Surface:
    """rotate an image while keeping its center and size"""
    orig_rect = original_image.get_rect()
    rot_image = pg.transform.rotate(original_image, angle_degrees)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

"""Utils."""

import logging

import pygame as pg


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    fmt = "%(asctime)s %(funcName)20s(): %(message)s"
    logging.basicConfig(level=log_level, format=fmt)
    return logging.getLogger()


def rot_center(original_image: pg.Surface, angle_degrees: float) -> pg.Surface:
    """Rotate an image while keeping its center and size."""
    orig_rect = original_image.get_rect()
    rot_image = pg.transform.rotate(original_image, angle_degrees)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    return rot_image.subsurface(rot_rect).copy()

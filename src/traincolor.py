"""Train color."""

from __future__ import annotations

from enum import Enum


class TrainColor(Enum):
    RED = "train_red"
    BLUE = "train_blue"
    YELLOW = "train_yellow"
    ORANGE = "train_orange"
    PURPLE = "train_purple"
    GREEN = "train_green"
    BROWN = "train_brown"


def color_as_short_string(color: TrainColor | str) -> str:
    if isinstance(color, TrainColor):
        return str(color).rsplit(".", maxsplit=1)[-1][0].lower()
    return ""


def blend_train_colors(color_1: TrainColor, color_2: TrainColor) -> TrainColor:
    if color_1 == color_2:
        return color_1
    colors = [color_1, color_2]
    if TrainColor.BLUE in colors and TrainColor.RED in colors:
        blended_train_color = TrainColor.PURPLE
    elif TrainColor.BLUE in colors and TrainColor.YELLOW in colors:
        blended_train_color = TrainColor.GREEN
    elif TrainColor.YELLOW in colors and TrainColor.RED in colors:
        blended_train_color = TrainColor.ORANGE
    else:
        blended_train_color = TrainColor.BROWN
    return blended_train_color

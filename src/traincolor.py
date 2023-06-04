from enum import Enum
from typing import Union

class TrainColor(Enum):
    RED = "train_red"
    BLUE = "train_blue"
    YELLOW = "train_yellow"

    ORANGE = "train_orange"
    PURPLE = "train_purple"
    GREEN = "train_green"

    BROWN = "train_brown"


def color_as_short_string(color: Union[TrainColor, str]) -> str:
    if isinstance(color, TrainColor):
        return str(color).rsplit(".", maxsplit=1)[-1][0].lower()
    return ""

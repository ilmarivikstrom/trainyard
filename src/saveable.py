from typing import Union
from src.traincolor import TrainColor, color_as_short_string


class SaveableAttributes:
    # TypeNumberColorOrientation
    # Examples:
    #  - D1y90
    #  - E
    #  - R
    #  - A4r90
    def __init__(self, block_type: str="", color: Union[TrainColor, str]="", number: Union[int, str]="", angle: Union[int, str]=""):
        self.block_type = block_type
        self.color = color_as_short_string(color)
        self.number = number
        self.angle = angle

    def serialize(self) -> str:
        return f"{self.block_type}{self.number}{self.color}{self.angle}"


class Saveable:
    def __init__(self, saveable_string: str):
        self.type = None
        self.num_goals = 0

        if len(saveable_string) == 1: # Case when e.g. "E"
            self.type = saveable_string
        else:
            self.type = saveable_string[0]
            self.num_goals = int(saveable_string[1])
            if saveable_string[2] == "r":
                self.color_goals = TrainColor.RED
            elif saveable_string[2] == "g":
                self.color_goals = TrainColor.GREEN
            elif saveable_string[2] == "b":
                self.color_goals = TrainColor.BLUE
            elif saveable_string[2] == "y":
                self.color_goals = TrainColor.YELLOW
            elif saveable_string[2] == "o":
                self.color_goals = TrainColor.ORANGE
            elif saveable_string[2] == "p":
                self.color_goals = TrainColor.PURPLE
            else:
                raise ValueError(f"Color is not valid. Expected one of TrainColor but got '{saveable_string[2]}'")
            self.angle = int(saveable_string[3:])

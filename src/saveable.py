from typing import Optional, Tuple
from src.train import TrainColor

class SaveableAttributes:
    # TypeNumberColor:Orientation:PosI,PosJ
    # Example:
    #  - D1y:90:3,4
    #  - E:0:4,4
    #  - R:0:6,7
    #  - A4r:90:7,7
    def __init__(self, block_type: str="", color: Optional[TrainColor]=None, number: Optional[int]=None, orientation: int=0, position: Optional[Tuple[int, int]]=None):
        self.block_type = block_type
        self.color = str(color).rsplit(".", maxsplit=1)[-1][0].lower() # TrainColor.YELLOW --> 'y'
        self.number = number
        self.orientation = orientation
        self.position = position

    def serialize(self) -> str:
        if self.position:
            return f"{self.block_type}{self.number}{self.color}:{self.orientation}:{self.position[0]},{self.position[1]}"
        raise ValueError("Position must be initialized to some actual value.")


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

"""Saveable."""

from __future__ import annotations

from src.traincolor import TrainColor, color_as_short_string


class SaveableAttributes:
    # TypeNumberColorOrientation
    # Examples: D1y90, E, R, A4r90
    def __init__(
        self,
        block_type: str = "",
        number: int | str = "",
        color: TrainColor | str = "",
        angle: int | str = "",
    ) -> None:
        self.block_type = block_type
        self.color = color_as_short_string(color)
        self.number = number
        self.angle = angle

    def serialize(self) -> str:
        return f"{self.block_type}{self.number}{self.color}{self.angle}"


class Saveable:
    def __init__(self, saveable_string: str) -> None:
        self.type = None
        self.num_goals = 0
        self.type = saveable_string[0]
        if len(saveable_string) == 1:  # Case when e.g. "E"
            self.type = saveable_string
            return
        if saveable_string[0] == "S":
            self.angle = int(saveable_string[1:])
        elif saveable_string[2] == "r":
            self.color = TrainColor.RED
            self.num_goals = int(saveable_string[1])
            self.angle = int(saveable_string[3:])
        elif saveable_string[2] == "g":
            self.color = TrainColor.GREEN
            self.num_goals = int(saveable_string[1])
            self.angle = int(saveable_string[3:])
        elif saveable_string[2] == "b":
            self.color = TrainColor.BLUE
            self.num_goals = int(saveable_string[1])
            self.angle = int(saveable_string[3:])
        elif saveable_string[2] == "y":
            self.color = TrainColor.YELLOW
            self.num_goals = int(saveable_string[1])
            self.angle = int(saveable_string[3:])
        elif saveable_string[2] == "o":
            self.color = TrainColor.ORANGE
            self.num_goals = int(saveable_string[1])
            self.angle = int(saveable_string[3:])
        elif saveable_string[2] == "p":
            self.color = TrainColor.PURPLE
            self.num_goals = int(saveable_string[1])
            self.angle = int(saveable_string[3:])
        else:  # Case when e.g. S0, P90
            self.angle = int(saveable_string[1:])

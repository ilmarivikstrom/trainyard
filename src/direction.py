from enum import Enum


class Direction(Enum):
    NONE = -1
    RIGHT = 0
    UP = 90
    LEFT = 180
    DOWN = 270
    RIGHTUP = 45
    UPLEFT = 135
    LEFTDOWN = 225
    RIGHTDOWN = 315

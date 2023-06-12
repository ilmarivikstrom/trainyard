from enum import Enum

from src.config import Config
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


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


def turn(old_dir: Direction, left: bool=False, right: bool=False) -> Direction:
    if (not left and not right) or (left and right):
        logger.error(f"Values for left and right were {left} and {right}. Returning Direction.NONE")
        return Direction.NONE
    elif old_dir == Direction.RIGHT:
        if left:
            return Direction.UP
        if right:
            return Direction.DOWN
    elif old_dir == Direction.UP:
        if left:
            return Direction.LEFT
        if right:
            return Direction.RIGHT
    elif old_dir == Direction.LEFT:
        if left:
            return Direction.DOWN
        if right:
            return Direction.UP
    elif old_dir == Direction.DOWN:
        if left:
            return Direction.RIGHT
        if right:
            return Direction.LEFT
    return Direction.NONE

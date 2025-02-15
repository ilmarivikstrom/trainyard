"""Direction."""

from enum import Enum

from src.config import Config
from src.utils.utils import setup_logging

logger = setup_logging(log_level=Config.LOG_LEVEL)


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


def turn_left(old_dir: Direction) -> Direction:
    if old_dir == Direction.RIGHT:
        return Direction.UP
    if old_dir == Direction.UP:
        return Direction.LEFT
    if old_dir == Direction.LEFT:
        return Direction.DOWN
    if old_dir == Direction.DOWN:
        return Direction.RIGHT
    return Direction.NONE


def turn_right(old_dir: Direction) -> Direction:
    if old_dir == Direction.RIGHT:
        return Direction.DOWN
    if old_dir == Direction.UP:
        return Direction.RIGHT
    if old_dir == Direction.LEFT:
        return Direction.UP
    if old_dir == Direction.DOWN:
        return Direction.LEFT
    return Direction.NONE

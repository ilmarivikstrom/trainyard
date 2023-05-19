import math
from enum import Enum

import pygame as pg

from src.config import Config
from src.controls import UserControl
from src.direction import Direction
from src.sound import Sound
from src.train import Train, TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)

class Phase(Enum):
    MAIN_MENU = 0
    GAMEPLAY = 1
    GAME_END = 2


class State:
    game_phase = Phase.MAIN_MENU
    screen_surface = None

    curr_cell = pg.Vector2(-1, -1)
    prev_cell = pg.Vector2(-1, -1)
    prev_cell_needs_checking = False
    curr_movement = Direction.NONE
    prev_movement = Direction.NONE

    trains = []
    trains_crashed = 0
    cell_sprites = pg.sprite.Group()
    train_sprites = pg.sprite.Group()
    angular_vel = (math.pi / 2) / 48 # With 48 ticks per 90 degrees...

    trains_released = False

    departure_stations = []
    arrival_stations = []
    departure_station_sprites = pg.sprite.Group()
    arrival_station_sprites = pg.sprite.Group()

    current_tick = 0

    level_passed = False

    gradient_dest = (0, 0)

    day_cycle_dest = [0, 0]

    @staticmethod
    def update_gameplay_state() -> None:
        UserControl.update_user_controls()

        if UserControl.pressed_keys[pg.K_SPACE] and not UserControl.wait_for_space_up:
            State.trains_released = not State.trains_released
            UserControl.wait_for_space_up = True
            logger.debug("Space down.")
        if UserControl.wait_for_space_up:
            if not UserControl.pressed_keys[pg.K_SPACE]:
                UserControl.wait_for_space_up = False
                logger.debug("Space released.")
        # TODO: Reset only once.
        if not State.trains_released:
            for departure_station in State.departure_stations:
                departure_station.reset()
            for arrival_station in State.arrival_stations:
                arrival_station.reset()
            State.trains.clear()
            State.train_sprites.empty()
            State.trains_crashed = 0
            State.trains_released = False
            State.level_passed = False


    @staticmethod
    def merge_trains(train_1: Train, train_2: Train) -> None:
        if train_1.color == train_2.color:
            upcoming_train_color = train_1.color
        else:
            colors = [train_1.color, train_2.color]
            if TrainColor.BLUE in colors and TrainColor.RED in colors:
                upcoming_train_color = TrainColor.PURPLE
            elif TrainColor.BLUE in colors and TrainColor.YELLOW in colors:
                upcoming_train_color = TrainColor.GREEN
            elif TrainColor.YELLOW in colors and TrainColor.RED in colors:
                upcoming_train_color = TrainColor.ORANGE
            else:
                raise ValueError("Need brown color...")
        train_1.paint(upcoming_train_color)
        State.trains.remove(train_2)
        train_2.kill()
        logger.info(f"Removed a train! Trains remaining: {len(State.trains)} or {len(State.train_sprites)}")
        Sound.play_sound_on_channel(Sound.merge, 0)

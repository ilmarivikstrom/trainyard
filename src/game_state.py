from enum import Enum
from typing import List

import pygame as pg

from src.config import Config
from src.controls import UserControl
from src.sound import Sound
from src.station import ArrivalStation, DepartureStation
from src.train import Train, TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)

class Phase(Enum):
    MAIN_MENU = 0
    GAMEPLAY = 1
    GAME_END = 2


class State:
    game_phase = Phase.MAIN_MENU
    screen_surface = pg.display.set_mode((Config.screen_width, Config.screen_height))
    trains: List[Train] = []
    trains_crashed = 0
    cell_sprites = pg.sprite.Group() # type: ignore
    train_sprites = pg.sprite.Group() # type: ignore
    trains_released = False
    departure_stations: List[DepartureStation] = []
    arrival_stations: List[ArrivalStation]= []
    departure_station_sprites = pg.sprite.Group() # type: ignore
    arrival_station_sprites = pg.sprite.Group() # type: ignore
    current_tick = 0
    level_passed = False
    gradient_dest: tuple[float, float] = (0.0, 0.0)
    day_cycle_dest: tuple[float, float] = (0.0, 0.0)
    prev_cell_needs_checking = False


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
                raise ValueError(f"Trains with colors: {colors} crashed. Need brown color...")
        train_1.paint(upcoming_train_color)
        State.trains.remove(train_2)
        train_2.kill()
        logger.info(f"Removed a train! Trains remaining: {len(State.trains)} or {len(State.train_sprites)}")
        Sound.play_sound_on_channel(Sound.merge, 0)

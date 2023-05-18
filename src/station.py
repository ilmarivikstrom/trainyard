import pygame as pg
from src.config import Config
from src.direction import Direction
from src.cell import Cell
from src.game_state import State
from src.resources import Resources
from src.sound import Sound
from src.train import Train, TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class Station(Cell):
    def __init__(self, i: int, j: int, image: pg.Surface, angle: int, number_of_trains: int, train_color: TrainColor):
        super().__init__(i, j, image, angle)
        self.train_color = train_color
        self.number_of_trains = number_of_trains
        self.original_number_of_trains = number_of_trains
        self.is_reset = False
        self.goals = []
        self.goal_sprites = pg.sprite.Group()
    
    def create_goal_sprites(self):
        self.goals = [StationGoalSprite("blue", i+1, self.rect) for i in range(self.number_of_trains)]
        self.goal_sprites.add(self.goals)


class StationGoalSprite(pg.sprite.Sprite):
    def __init__(self, color: str, place: int, parent_rect: pg.Rect):
        super().__init__()
        self.image = Resources.img_surfaces[f"{color}_train_{place}"]
        self.rect = parent_rect

class DepartureStation(Station):
    def __init__(self, i: int, j: int, angle: int, number_of_trains: int, train_color: TrainColor):
        super().__init__(i, j, Resources.img_surfaces["departure"], angle, number_of_trains, train_color)

        self.create_goal_sprites()

        self.last_release_tick = None
        self.saveable_attributes = SaveableAttributes(self)

    def update(self):
        if State.trains_released and self.number_of_trains > 0:
            self.is_reset = False
            if not self.last_release_tick or State.current_tick - self.last_release_tick == 32:
                train_to_release = Train(self.i, self.j, self.train_color, Direction(self.angle))
                State.trains.append(train_to_release)
                State.train_sprites.add(train_to_release)
                self.number_of_trains -= 1
                self.goals.pop().kill() # Remove from list and kill the departure sprite.
                logger.debug("Train released.")
                self.last_release_tick = State.current_tick
                Sound.play_sound_on_channel(Sound.pop, 1)
                logger.info(f"Departure station saveable attributes: {self.saveable_attributes.serialize()}")


    def reset(self):
        if not self.is_reset:
            self.number_of_trains = self.original_number_of_trains
            self.goal_sprites.empty()
            self.create_goal_sprites()
            self.is_reset = True
            self.last_release_tick = None



class ArrivalStation(Station):
    def __init__(self, i: int, j: int, angle: int, number_of_trains: int, train_color: TrainColor):
        super().__init__(i, j, Resources.img_surfaces["arrival"], angle, number_of_trains, train_color)
        self.saveable_attributes = SaveableAttributes(self)

    def handle_train_arrival(self, train):
        if train.color == self.train_color and self.goals and self.number_of_trains > 0:
            self.is_reset = False
            self.number_of_trains -= 1
            self.goals.pop().kill()
            logger.debug(f"Caught a train! Number of trains still expecting: {self.number_of_trains}")
            Sound.play_sound_on_channel(Sound.pop, 1)
        else:
            logger.debug("CRASH! Wrong color train or not expecting further arrivals.")
            train.crash()
            State.trains_crashed += 1
        train.kill()
        State.trains.remove(train)


    def reset(self):
        if not self.is_reset:
            self.number_of_trains = self.original_number_of_trains
            self.goal_sprites.empty()
            self.create_goal_sprites()
            self.is_reset = True


class SaveableAttributes:
    block_types = {
        ArrivalStation: "A",
        DepartureStation: "D",
    }
    block_colors = {
        TrainColor.BLUE: "b",
        TrainColor.RED: "r",
        TrainColor.YELLOW: "y",
        None: "",
    }
    # Example:
    # TypeNumberColor:Orientation:PosI,PosJ
    # D1y:90:3,4
    # E:0:4,4
    # R:0:6,7
    # A4r:90:7,7
    def __init__(self, block):
        self.type = self.block_types[type(block)]
        self.color = self.block_colors[None]
        self.number = None
        if isinstance(block, (ArrivalStation, DepartureStation)):
            self.color = self.block_colors[block.train_color]
            self.number = block.number_of_trains
        self.orientation = block.angle
        self.position = (block.i, block.j)

    def serialize(self):
        return f"{self.type}{self.number}{self.color}:{self.orientation}:{self.position[0]},{self.position[1]}"

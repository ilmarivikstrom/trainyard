import pygame as pg
from src.config import Config
from src.direction import Direction
from src.cell import Cell
from src.game_state import State
from src.resources import Resources
from src.sound import Sound
from src.train import Train, TrainColor
from src.utils import setup_logging, SaveableAttributes

logger = setup_logging(log_level=Config.log_level)

class StationGoalSprite(pg.sprite.Sprite):
    def __init__(self, color: str, place: int, parent_rect: pg.Rect):
        super().__init__()
        self.image = Resources.img_surfaces[f"{color}_train_{place}"]
        self.rect = parent_rect


class Station(Cell):
    def __init__(self, i: int, j: int, image: pg.Surface, angle: int, number_of_trains_left: int, train_color: TrainColor, block_short_char: str):
        super().__init__(i, j, image, angle)
        self.number_of_trains_left = number_of_trains_left
        self.train_color = train_color
        self.block_short_char = block_short_char
        self.original_number_of_trains = number_of_trains_left
        self.is_reset = False
        self.goals = []
        self.goal_sprites = pg.sprite.Group()
        self.last_release_tick = None
        self.saveable_attributes = SaveableAttributes(block_type=self.block_short_char, color=self.train_color, number=self.number_of_trains_left, orientation=self.angle, position=(self.i, self.j))
        self.create_goal_sprites()

    def create_goal_sprites(self):
        self.goals = [StationGoalSprite("blue", i+1, self.rect) for i in range(self.number_of_trains_left)]
        self.goal_sprites.add(self.goals)

    def reset(self):
        if not self.is_reset:
            self.number_of_trains_left = self.original_number_of_trains
            self.goal_sprites.empty()
            self.create_goal_sprites()
            self.is_reset = True
            self.last_release_tick = None



class DepartureStation(Station):
    def __init__(self, i: int, j: int, angle: int, number_of_trains_left: int, train_color: TrainColor):
        super().__init__(i=i, j=j, image=Resources.img_surfaces["departure"], angle=angle, number_of_trains_left=number_of_trains_left, train_color=train_color, block_short_char="D")

    def update(self):
        if State.trains_released and self.number_of_trains_left > 0:
            self.is_reset = False
            if not self.last_release_tick or State.current_tick - self.last_release_tick == 32:
                train_to_release = Train(self.i, self.j, self.train_color, Direction(self.angle))
                State.trains.append(train_to_release)
                State.train_sprites.add(train_to_release)
                self.number_of_trains_left -= 1
                self.goals.pop().kill()
                logger.debug("Train released.")
                self.last_release_tick = State.current_tick
                Sound.play_sound_on_channel(Sound.pop, 1)
                logger.info(f"Departure station saveable attributes: {self.saveable_attributes.serialize()}")



class ArrivalStation(Station):
    def __init__(self, i: int, j: int, angle: int, number_of_trains_left: int, train_color: TrainColor):
        super().__init__(i=i, j=j, image=Resources.img_surfaces["arrival"], angle=angle, number_of_trains_left=number_of_trains_left, train_color=train_color, block_short_char="A")

    def handle_train_arrival(self, train):
        if train.color == self.train_color and self.goals and self.number_of_trains_left > 0:
            self.is_reset = False
            self.number_of_trains_left -= 1
            self.goals.pop().kill()
            logger.debug(f"Caught a train! Number of trains still expecting: {self.number_of_trains_left}")
            Sound.play_sound_on_channel(Sound.pop, 1)
        else:
            logger.debug("CRASH! Wrong color train or not expecting further arrivals.")
            train.crash()
            State.trains_crashed += 1
        train.kill()
        State.trains.remove(train)

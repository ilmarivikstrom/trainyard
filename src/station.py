import pygame as pg
from src.config import Config
from src.direction import Direction
from src.game_state import State
from src.resources import Resources
from src.sound import Sound
from src.train import Train, TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)

class DepartureSprite(pg.sprite.Sprite):
    def __init__(self, color: str, place: int, parent_rect: pg.Rect):
        super().__init__()
        self.image = Resources.img_surfaces[f"{color}_train_{place}"]
        self.rect = parent_rect


class DepartureStation(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, angle: float, number_of_trains_to_release: int, train_color: TrainColor):
        super().__init__()
        self.i = i
        self.j = j
        self.angle = angle
        self.number_of_trains_to_release = number_of_trains_to_release
        self.train_color = train_color

        self.original_number_of_trains_to_release = number_of_trains_to_release

        self.image = pg.transform.rotate(Resources.img_surfaces["departure"], self.angle)

        self.rect = self.image.get_rect()
        self.rect.x = i * Config.cell_size + Config.padding_x
        self.rect.y = j * Config.cell_size + Config.padding_y

        self.departures = []
        self.departure_sprites = pg.sprite.Group()

        self.create_departure_sprites()

        self.is_reset = True

        self.last_release_tick = None


    def update(self):
        if State.trains_released:
            if self.number_of_trains_to_release > 0:
                self.is_reset = False
                if self.last_release_tick is None or State.current_tick - self.last_release_tick == 32:
                    train_to_release = Train(self.i, self.j, self.train_color, Direction.UP)
                    State.trains.append(train_to_release)
                    State.train_sprites.add(train_to_release)
                    self.number_of_trains_to_release -= 1
                    # Kill the departure sprite.
                    self.departures[-1].kill()
                    self.departures.pop(-1)
                    logger.debug("Train released.")
                    self.last_release_tick = State.current_tick
                    Sound.pop.play()


    def reset(self):
        if not self.is_reset:
            self.number_of_trains_to_release = self.original_number_of_trains_to_release
            self.departure_sprites.empty()
            self.create_departure_sprites()
            self.is_reset = True
            self.last_release_tick = None

    def create_departure_sprites(self):
        self.departures = [DepartureSprite("blue", i+1, self.rect) for i in range(self.number_of_trains_to_release)]
        self.departure_sprites.add(self.departures)



class ArrivalStation(pg.sprite.Sprite):
    def __init__(self, i: int, j: int, angle: int, number_of_trains_to_catch: int, train_color: TrainColor):
        super().__init__()
        self.i = i
        self.j = j
        self.angle = angle
        self.number_of_trains_to_catch = number_of_trains_to_catch
        self.train_color = train_color

        self.original_number_of_trains_to_catch = number_of_trains_to_catch

        self.image = pg.transform.rotate(Resources.img_surfaces["arrival"], self.angle)

        self.arrivals = []
        self.arrival_sprites = pg.sprite.Group()

        self.rect = self.image.get_rect()
        self.rect.x = i * Config.cell_size + Config.padding_x
        self.rect.y = j * Config.cell_size + Config.padding_y

        self.is_reset = False

    def catch(self, train):
        if train.color == self.train_color and len(self.arrivals) > 0 and self.number_of_trains_to_catch > 0:
            self.is_reset = False
            self.number_of_trains_to_catch -= 1
            self.arrivals[-1].kill()
            self.arrivals.pop(-1)
            logger.debug(f"Caught a train! Number of trains still expecting: {self.number_of_trains_to_catch}")
            Sound.pop.play()
        else:
            logger.debug("CRASH! Wrong color train or not expecting further arrivals.")
            train.crash()
            State.trains_crashed += 1
        train.kill()
        State.trains.remove(train)

    def reset(self):
        if not self.is_reset:
            self.number_of_trains_to_catch = self.original_number_of_trains_to_catch
            self.arrival_sprites.empty()
            self.create_arrival_sprites()
            self.is_reset = True


    def create_arrival_sprites(self):
        self.arrivals = [DepartureSprite("blue", i+1, self.rect) for i in range(self.number_of_trains_to_catch)]
        self.arrival_sprites.add(self.arrivals)

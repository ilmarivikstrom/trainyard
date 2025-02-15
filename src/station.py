"""Station."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from src.cell import Cell
from src.config import Config
from src.direction import Direction
from src.graphics import Graphics
from src.saveable import SaveableAttributes
from src.sound import Sound
from src.track import InsideTrack, Track, TrackType
from src.train import Train
from src.traincolor import TrainColor
from src.utils import setup_logging

if TYPE_CHECKING:
    from src.coordinate import Coordinate

logger = setup_logging(log_level=Config.log_level)


class StationGoalSprite(pg.sprite.Sprite):
    def __init__(self, color: str, place: int, parent_rect: pg.Rect) -> None:
        super().__init__()
        self.image = Graphics.img_surfaces[f"{color}_goal_{place}"]
        self.rect = parent_rect


class CheckmarkSprite(pg.sprite.Sprite):
    def __init__(self, parent_rect: pg.Rect) -> None:
        super().__init__()
        self.image = Graphics.img_surfaces["checkmark"]
        self.rect = parent_rect


class Station(Cell):
    def __init__(
        self,
        coords: Coordinate,
        image: pg.Surface,
        angle: int,
        number_of_trains_left: int,
        train_color: TrainColor,
        block_short_char: str,
    ) -> None:
        super().__init__(coords, image, angle)
        self.number_of_trains_left = number_of_trains_left
        self.train_color = train_color
        self.original_number_of_trains = number_of_trains_left
        self.block_short_char = block_short_char
        self.goals: list[StationGoalSprite] = []
        self.goal_sprites = pg.sprite.Group()  # type: ignore
        self.checkmark: CheckmarkSprite | None = None
        self.last_release_tick: int | None = None
        self.saveable_attributes = SaveableAttributes(
            block_type=self.block_short_char,
            color=self.train_color,
            number=self.number_of_trains_left,
            angle=self.angle,
        )

        if self.angle in [0, 180]:
            self.tracks: list[Track | InsideTrack] = [
                InsideTrack(self.pos, self.rect, TrackType.HORI, self.angle),
            ]
        elif self.angle in [90, 270]:
            self.tracks: list[Track | InsideTrack] = [
                InsideTrack(self.pos, self.rect, TrackType.VERT, self.angle),
            ]
        else:
            msg = "Station's angle is incompatible with placing InsideTracks."
            raise ValueError(
                msg,
            )
        self.create_goal_sprites()

    def create_goal_sprites(self) -> None:
        if self.train_color == TrainColor.BLUE:
            goal_sprite_color = "blue"
        elif self.train_color == TrainColor.RED:
            goal_sprite_color = "red"
        elif self.train_color == TrainColor.YELLOW:
            goal_sprite_color = "yellow"
        elif self.train_color == TrainColor.ORANGE:
            goal_sprite_color = "orange"
        elif self.train_color == TrainColor.GREEN:
            goal_sprite_color = "green"
        elif self.train_color == TrainColor.PURPLE:
            goal_sprite_color = "purple"
        else:
            msg = f"Missing goal sprite string for color {self.train_color}"
            raise ValueError(msg)
        if self.rect:
            self.goals = [
                StationGoalSprite(goal_sprite_color, i + 1, self.rect)
                for i in range(self.number_of_trains_left)
            ]
            self.goal_sprites.add(self.goals)  # type: ignore

    def reset(self) -> None:
        self.number_of_trains_left = self.original_number_of_trains
        self.goal_sprites.empty()  # type: ignore
        self.create_goal_sprites()
        self.last_release_tick = None
        self.checkmark = None


class DepartureStation(Station):
    def __init__(
        self,
        coords: Coordinate,
        angle: int,
        number_of_trains_left: int,
        train_color: TrainColor,
    ) -> None:
        super().__init__(
            coords=coords,
            image=Graphics.img_surfaces["departure"],
            angle=angle,
            number_of_trains_left=number_of_trains_left,
            train_color=train_color,
            block_short_char="D",
        )

    def tick(self, current_tick: int) -> Train | None:
        station_needs_to_release = self.number_of_trains_left > 0 and (
            self.last_release_tick is None
            or current_tick - self.last_release_tick == 64
        )
        if not station_needs_to_release:
            return None
        self.number_of_trains_left -= 1
        self.goals.pop().kill()
        logger.debug("Train released.")
        self.last_release_tick = current_tick
        Sound.play_sound_on_any_channel(Sound.pop)
        return Train(self.pos, self.train_color, self.tracks[0], Direction(self.angle))


class ArrivalStation(Station):
    def __init__(
        self,
        coords: Coordinate,
        angle: int,
        number_of_trains_left: int,
        train_color: TrainColor,
    ) -> None:
        super().__init__(
            coords=coords,
            image=Graphics.img_surfaces["arrival"],
            angle=angle,
            number_of_trains_left=number_of_trains_left,
            train_color=train_color,
            block_short_char="A",
        )

"""Train."""

import math

import pygame as pg

from src.cell import Cell, DrawingCell
from src.config import Config
from src.coordinate import Coordinate
from src.direction import Direction
from src.graphics import Graphics
from src.sound import Sound
from src.track import Track, TrackType
from src.traincolor import TrainColor
from src.utils import rot_center


class Train(pg.sprite.Sprite):
    def __init__(
        self,
        coords: Coordinate,
        color: TrainColor,
        selected_track: Track,
        direction: Direction,
    ) -> None:
        super().__init__()
        self.loc = coords
        self.color: TrainColor = color
        self.direction: Direction = direction

        self.image: pg.Surface = Graphics.img_surfaces[color.value]
        self.original_image: pg.Surface = self.image
        self.rect: pg.Rect = self.image.get_rect()  # type: ignore

        self.rect.x = int(
            self.loc.x * Config.cell_size
            - 0.5 * Config.cell_size
            + Config.padding_x
            + 48
        )  # TODO: Get the location from somewhere else please.
        self.rect.y = (
            self.loc.y * Config.cell_size + Config.padding_y + 16
        )  # TODO: Get the location from somewhere else please.

        self.original_direction: Direction = direction
        self.angle: float = self.direction.value
        self.last_collided_cells: list[Cell] = []
        self.last_flipped_cell: DrawingCell | None = None

        self.selected_track: Track | None = selected_track

        self.next_cell_coords: tuple[int, int] = (0, 0)
        self.next_cell_direction: Direction = Direction.RIGHT

        self.original_pos = (self.rect.x, self.rect.y)
        self.crashed = False

        self.current_navigation_index = 32
        self.determine_next_cell_coords_and_direction()

    def determine_next_cell_coords_and_direction(self) -> None:
        if self.selected_track is None:
            raise ValueError("Selected track is None.")
        if self.direction == Direction.UP:
            if self.selected_track.track_type == TrackType.VERT:
                self.next_cell_coords = (
                    self.selected_track.pos.x,
                    self.selected_track.pos.y - 1,
                )
                self.next_cell_direction = Direction.UP
            elif self.selected_track.track_type == TrackType.BOTTOM_LEFT:
                self.next_cell_coords = (
                    self.selected_track.pos.x - 1,
                    self.selected_track.pos.y,
                )
                self.next_cell_direction = Direction.LEFT
            elif self.selected_track.track_type == TrackType.BOTTOM_RIGHT:
                self.next_cell_coords = (
                    self.selected_track.pos.x + 1,
                    self.selected_track.pos.y,
                )
                self.next_cell_direction = Direction.RIGHT
            else:
                raise ValueError("Bad tracktype and/or direction.")
        elif self.direction == Direction.DOWN:
            if self.selected_track.track_type == TrackType.VERT:
                self.next_cell_coords = (
                    self.selected_track.pos.x,
                    self.selected_track.pos.y + 1,
                )
                self.next_cell_direction = Direction.DOWN
            elif self.selected_track.track_type == TrackType.TOP_LEFT:
                self.next_cell_coords = (
                    self.selected_track.pos.x - 1,
                    self.selected_track.pos.y,
                )
                self.next_cell_direction = Direction.LEFT
            elif self.selected_track.track_type == TrackType.TOP_RIGHT:
                self.next_cell_coords = (
                    self.selected_track.pos.x + 1,
                    self.selected_track.pos.y,
                )
                self.next_cell_direction = Direction.RIGHT
            else:
                raise ValueError("Bad tracktype and/or direction.")
        elif self.direction == Direction.RIGHT:
            if self.selected_track.track_type == TrackType.HORI:
                self.next_cell_coords = (
                    self.selected_track.pos.x + 1,
                    self.selected_track.pos.y,
                )
                self.next_cell_direction = Direction.RIGHT
            elif self.selected_track.track_type == TrackType.TOP_LEFT:
                self.next_cell_coords = (
                    self.selected_track.pos.x,
                    self.selected_track.pos.y - 1,
                )
                self.next_cell_direction = Direction.UP
            elif self.selected_track.track_type == TrackType.BOTTOM_LEFT:
                self.next_cell_coords = (
                    self.selected_track.pos.x,
                    self.selected_track.pos.y + 1,
                )
                self.next_cell_direction = Direction.DOWN
            else:
                raise ValueError("Bad tracktype and/or direction.")
        elif self.direction == Direction.LEFT:
            if self.selected_track.track_type == TrackType.HORI:
                self.next_cell_coords = (
                    self.selected_track.pos.x - 1,
                    self.selected_track.pos.y,
                )
                self.next_cell_direction = Direction.LEFT
            elif self.selected_track.track_type == TrackType.TOP_RIGHT:
                self.next_cell_coords = (
                    self.selected_track.pos.x,
                    self.selected_track.pos.y - 1,
                )
                self.next_cell_direction = Direction.UP
            elif self.selected_track.track_type == TrackType.BOTTOM_RIGHT:
                self.next_cell_coords = (
                    self.selected_track.pos.x,
                    self.selected_track.pos.y + 1,
                )
                self.next_cell_direction = Direction.DOWN
            else:
                raise ValueError("Bad tracktype and/or direction.")

    def reset(self) -> None:
        self.rect.x = self.original_pos[0]
        self.rect.y = self.original_pos[1]
        self.image = self.original_image
        self.angle = 0
        self.direction = self.original_direction
        self.last_collided_cells = []
        self.last_flipped_cell = None

    def repaint(self, train_color: TrainColor) -> None:
        if self.color == TrainColor.BROWN:
            return
        self.color = train_color
        self.image = Graphics.img_surfaces[self.color.value]
        self.original_image = self.image

    def move(self) -> None:
        self.image = rot_center(self.original_image, self.angle)

        num_navigation_indices = 64

        if self.crashed:
            return
        if self.selected_track is None:
            raise ValueError("Selected track is None.")
        if self.selected_track.track_type == TrackType.VERT:
            if (
                self.direction == Direction.DOWN
                or round(self.angle) == Direction.DOWN.value
            ):
                self.angle = Direction.DOWN.value
                self.rect.centerx += self.selected_track.navigation[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation[
                    self.current_navigation_index
                ][1]
            elif (
                self.direction == Direction.UP
                or round(self.angle) == Direction.UP.value
            ):
                self.angle = Direction.UP.value
                self.rect.centerx += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][1]
            else:
                raise ValueError("Bad direction.")
            self.current_navigation_index += 1
        elif self.selected_track.track_type == TrackType.HORI:
            if (
                self.direction == Direction.RIGHT
                or round(self.angle) == Direction.RIGHT.value
            ):
                self.angle = Direction.RIGHT.value
                self.rect.centerx += self.selected_track.navigation[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation[
                    self.current_navigation_index
                ][1]
            elif (
                self.direction == Direction.LEFT
                or round(self.angle) == Direction.LEFT.value
            ):
                self.angle = Direction.LEFT.value
                self.rect.centerx += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][1]
            else:
                raise ValueError("Bad direction.")
            self.current_navigation_index += 1
        elif self.selected_track.track_type == TrackType.TOP_LEFT:
            if (
                self.direction == Direction.RIGHT
                or round(self.angle) == Direction.RIGHT.value
            ):
                self.angle = Direction.RIGHT.value + math.degrees(
                    0.5
                    * math.pi
                    * math.sin(
                        0.5
                        * math.pi
                        * (self.current_navigation_index / num_navigation_indices)
                    )
                )
                self.rect.centerx += self.selected_track.navigation[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation[
                    self.current_navigation_index
                ][1]
            elif (
                self.direction == Direction.DOWN
                or round(self.angle) == Direction.DOWN.value
            ):
                self.angle = Direction.DOWN.value - math.degrees(
                    0.5
                    * math.pi
                    * math.sin(
                        0.5
                        * math.pi
                        * (self.current_navigation_index / num_navigation_indices)
                    )
                )
                self.rect.centerx += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][1]
            else:
                raise ValueError("Bad direction.")
            self.current_navigation_index += 1
        elif self.selected_track.track_type == TrackType.TOP_RIGHT:
            if (
                self.direction == Direction.DOWN
                or round(self.angle) == Direction.DOWN.value
            ):
                self.angle = Direction.DOWN.value + math.degrees(
                    0.5
                    * math.pi
                    * math.sin(
                        0.5
                        * math.pi
                        * (self.current_navigation_index / num_navigation_indices)
                    )
                )
                self.rect.centerx += self.selected_track.navigation[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation[
                    self.current_navigation_index
                ][1]
            elif (
                self.direction == Direction.LEFT
                or round(self.angle) == Direction.LEFT.value
            ):
                self.angle = Direction.LEFT.value - math.degrees(
                    0.5
                    * math.pi
                    * math.sin(
                        0.5
                        * math.pi
                        * (self.current_navigation_index / num_navigation_indices)
                    )
                )
                self.rect.centerx += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][1]
            else:
                raise ValueError("Bad direction.")
            self.current_navigation_index += 1
        elif self.selected_track.track_type == TrackType.BOTTOM_LEFT:
            if (
                self.direction == Direction.RIGHT
                or round(self.angle) == Direction.RIGHT.value
            ):
                self.angle = Direction.RIGHT.value - math.degrees(
                    0.5
                    * math.pi
                    * math.sin(
                        0.5
                        * math.pi
                        * (self.current_navigation_index / num_navigation_indices)
                    )
                )
                self.rect.centerx += self.selected_track.navigation[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation[
                    self.current_navigation_index
                ][1]
            elif (
                self.direction == Direction.UP
                or round(self.angle) == Direction.UP.value
            ):
                self.angle = Direction.UP.value + math.degrees(
                    0.5
                    * math.pi
                    * math.sin(
                        0.5
                        * math.pi
                        * (self.current_navigation_index / num_navigation_indices)
                    )
                )
                self.rect.centerx += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][1]
            else:
                raise ValueError("Bad direction.")
            self.current_navigation_index += 1
        elif self.selected_track.track_type == TrackType.BOTTOM_RIGHT:
            if (
                self.direction == Direction.UP
                or round(self.angle) == Direction.UP.value
            ):
                self.angle = Direction.UP.value - math.degrees(
                    0.5
                    * math.pi
                    * math.sin(
                        0.5
                        * math.pi
                        * (self.current_navigation_index / num_navigation_indices)
                    )
                )
                self.rect.centerx += self.selected_track.navigation[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation[
                    self.current_navigation_index
                ][1]
            elif (
                self.direction == Direction.LEFT
                or round(self.angle) == Direction.LEFT.value
            ):
                self.angle = Direction.LEFT.value + math.degrees(
                    0.5
                    * math.pi
                    * math.sin(
                        0.5
                        * math.pi
                        * (self.current_navigation_index / num_navigation_indices)
                    )
                )
                self.rect.centerx += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][0]
                self.rect.centery += self.selected_track.navigation_reversed[
                    self.current_navigation_index
                ][1]
            else:
                raise ValueError("Bad direction.")
            self.current_navigation_index += 1

    def tick(self, trains_released: bool) -> None:
        if trains_released:
            self.move()
        else:
            self.reset()

    def crash(self) -> None:
        self.selected_track = None
        self.crashed = True
        Sound.play_sound_on_any_channel(Sound.crash)

    def add_last_collided_cell(self, drawing_cell: Cell) -> None:
        self.last_collided_cells.append(drawing_cell)
        self.last_collided_cells = self.last_collided_cells[-2:]

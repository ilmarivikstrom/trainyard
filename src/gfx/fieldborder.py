"""Field border."""

import pygame as pg
from pygame.locals import SRCALPHA


class FieldBorder:
    def __init__(
        self,
        color: tuple[int, int, int],
        topleft: tuple[int, int],
        width: int,
        height: int,
        thickness: int,
    ) -> None:
        self.color: tuple[int, int, int] = color
        self.topleft: tuple[int, int] = topleft
        self.width: int = width
        self.height: int = height
        self._thickness: int = thickness
        self.surface: pg.Surface = pg.Surface((0, 0))
        self.calculate_position()

    def calculate_position(self) -> None:
        self.surface = pg.Surface(
            (self.width + 2 * self._thickness, self.height + 2 * self._thickness),
            SRCALPHA,
        )
        self.rect = (
            0,
            0,
            self.width + 2 * self._thickness,
            self.height + 2 * self._thickness,
        )
        self.location = (
            self.topleft[0] - 1 * self._thickness,
            self.topleft[1] - 1 * self._thickness,
        )

    def set_thickness(self, thickness: int) -> None:
        self._thickness = thickness
        self.calculate_position()

    def draw(self, screen_surface: pg.Surface) -> None:
        pg.draw.rect(self.surface, self.color, self.rect, self._thickness)
        screen_surface.blit(self.surface, self.location)

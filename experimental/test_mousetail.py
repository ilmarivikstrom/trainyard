import sys
from typing import List, Tuple

import pygame as pg
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, K_SPACE

clock = pg.time.Clock()

pg.init()
pg.display.set_caption("game base")
screen = pg.display.set_mode((500, 500), 0, 32)


TRAIN_RED = (192, 35, 97, 255)
TRAIN_BLUE = (73, 136, 161, 255)
TRAIN_YELLOW = (250, 194, 30, 255)
TRAIN_GREEN = (143, 198, 89, 255)
TRAIN_PURPLE = (109, 49, 138, 255)
TRAIN_ORANGE = (253, 54, 23, 255)
TRAIN_BROWN = (120, 68, 33, 255)


def dim_surface(surface: pg.Surface, dim_speed: int) -> None:
    surface.set_alpha(surface.get_alpha() - dim_speed)
    return surface


class MouseTail:
    def __init__(
        self, loc: Tuple[int, int], prev_loc: Tuple[int, int], speed: float, color: Tuple[int, int, int]
    ) -> None:
        self.loc = loc
        self.prev_loc = prev_loc
        self.speed = speed
        self.color = color
        self.alive = True
        self.ticks_to_die = 60 / self.speed
        self.color_jumps = (
            int(self.color[0] / self.ticks_to_die),
            int(self.color[1] / self.ticks_to_die),
            int(self.color[2] / self.ticks_to_die),
        )

    def tick(self) -> None:
        self.color = (
            self.color[0] - self.color_jumps[0],
            self.color[1] - self.color_jumps[1],
            self.color[2] - self.color_jumps[2],
        )
        if self.color[0] <= 0 or self.color[1] <= 0 or self.color[2] <= 0:
            self.alive = False

    def draw(self, screen: pg.Surface) -> None:
        if self.alive:
            pg.draw.line(screen, self.color, self.prev_loc, self.loc)


class Shockwave:
    def __init__(
        self, loc: Tuple[int, int], speed: float, color: Tuple[int, int, int, int], radius: float, width: int
    ) -> None:
        self.loc = loc
        self.speed = speed
        self.color = color
        self.radius = radius
        self.width = width
        self.alive = True

    def tick(self, delta_time: float) -> None:
        if self.speed < 0:
            color_decrease = 20
            self.color = (
                self.color[0] - color_decrease,
                self.color[1] - color_decrease,
                self.color[2] - color_decrease,
            )
            if self.color[0] <= 0:
                self.alive = False
        else:
            self.radius = self.radius + self.speed * delta_time
            self.speed -= 0.5

    def draw(self, screen: pg.Surface) -> None:
        if self.alive:
            print(self.color)
            pg.draw.circle(screen, self.color, self.loc, self.radius, self.width)


mouse_tails: List[MouseTail] = []
shock_waves: List[Shockwave] = []

iteration = 0

prev_mx, prev_my = pg.mouse.get_pos()

while True:
    screen.fill((0, 0, 0))

    curr_mx, curr_my = pg.mouse.get_pos()

    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pg.quit()
                sys.exit()

    if pg.mouse.get_pressed()[0] and (curr_mx != prev_mx or curr_my != prev_my):
        if pg.key.get_pressed()[pg.K_LSHIFT]:
            tail_color = TRAIN_RED
        else:
            tail_color = TRAIN_YELLOW
        mouse_tails.append(MouseTail(loc=(curr_mx, curr_my), prev_loc=(prev_mx, prev_my), speed=1, color=tail_color))
        if iteration % 25 == 0:
            shock_waves.append(Shockwave(loc=(curr_mx, curr_my), speed=10, color=(255, 255, 255), radius=10, width=5))
            # shock_waves.append(Shockwave(loc=(curr_mx, curr_my), speed=5, color=TRAIN_RED, radius=5, width=5))

    for i, mouse_tail in sorted(enumerate(mouse_tails), reverse=True):
        mouse_tail.tick()
        mouse_tail.draw(screen)
        if not mouse_tail.alive:
            mouse_tails.pop(i)

    for i, shock_wave in sorted(enumerate(shock_waves), reverse=True):
        shock_wave.tick(1)
        shock_wave.draw(screen)
        if not shock_wave.alive:
            shock_waves.pop(i)

    prev_mx = curr_mx
    prev_my = curr_my
    iteration += 1

    pg.display.update()
    clock.tick(60)

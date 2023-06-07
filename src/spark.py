import math
import random
from typing import List, Optional, Tuple

import pygame as pg

class Spark():
    def __init__(self, loc: List[int], angle: float, speed: float, color: Tuple[int, int, int], scale: float=1.0):
        self.loc: List[int] = loc
        self.angle: float = angle
        self.speed: float = speed
        self.scale: float = scale
        self.color: Tuple[int, int, int] = color
        self.alive: bool = True


    def calculate_movement(self, delta_time: float, allowed_area: pg.Rect, collide_rects: Optional[List[pg.Rect]]) -> Tuple[float, float]:
        if not allowed_area.collidepoint(self.loc):
            self.angle = 180 + self.angle
        else:
            for collide_rect in collide_rects:
                if collide_rect.collidepoint(self.loc):
                    self.angle = 180 + self.angle
                    break
        return (
            math.cos(self.angle) * 1.0 * self.speed * delta_time,
            math.sin(self.angle) * 1.0 * self.speed * delta_time
        )


    def move(self, delta_time: float, allowed_area: pg.Rect, collide_rects: Optional[List[pg.Rect]]):
        movement = self.calculate_movement(delta_time, allowed_area, collide_rects)
        self.loc[0] += movement[0]
        self.loc[1] += movement[1]
        self.speed -= 0.1
        if self.speed <= 0:
            self.alive = False
        #self.point_towards(math.pi / 2, 0.02)
        #self.velocity_adjust(0.9, 0, 8, delta_time)
        #self.angle += 0.1


    # def velocity_adjust(self, friction: float, force: float, terminal_velocity: float, delta_time: float):
    #     movement = self.calculate_movement(delta_time)
    #     movement = (min(terminal_velocity, movement[1] + force * delta_time), movement[0] * friction)
    #     self.angle = math.atan2(movement[1], movement[0])


    # def point_towards(self, angle: float, rate: float) -> None:
    #     rotate_direction = ((angle - self.angle + math.pi * 3) % (math.pi * 2)) - math.pi
    #     rotate_sign = abs(rotate_direction) / rotate_direction
    #     if abs(rotate_direction) < rate:
    #         self.angle = angle
    #     else:
    #         self.angle += rate * rotate_sign


    def draw(self, surf: pg.Surface):
        if self.alive:
            points = [
                [self.loc[0] + math.cos(self.angle) * self.speed * self.scale, self.loc[1] + math.sin(self.angle) * self.speed * self.scale],
                [self.loc[0] + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.3, self.loc[1] + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                [self.loc[0] - math.cos(self.angle) * self.speed * self.scale * 3.5, self.loc[1] - math.sin(self.angle) * self.speed * self.scale * 3.5],
                [self.loc[0] + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.3, self.loc[1] - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                ]
            pg.draw.polygon(surf, self.color, points)

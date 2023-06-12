import math
import random
from typing import List, Optional, Tuple

import pygame as pg

from src.sound import Sound

class Spark():
    def __init__(self, loc: List[int], angle: float, base_speed: float, friction: float, color: Tuple[int, int, int], scale: float=1.0, speed_multiplier: float=1.0):
        self.loc: List[int] = loc
        self.angle: float = angle
        self.base_speed: float = base_speed
        self.friction: float = friction
        self.scale: float = scale
        self.color: Tuple[int, int, int] = color
        self.alive: bool = True
        self.last_collision: List[int] = loc
        self.speed_multiplier: float = speed_multiplier


    def calculate_distance_to_move(self, delta_time: float) -> Tuple[float, float]:
        return (
            math.cos(self.angle) * self.speed_multiplier * self.base_speed * delta_time,
            math.sin(self.angle) * self.speed_multiplier * self.base_speed * delta_time
        )


    def bounce_from_edge(self, allowed_area: pg.Rect, collide_rects: Optional[List[pg.Rect]]) -> None:
        bounced = False
        if not allowed_area.collidepoint(self.loc):
            to_top = abs(self.loc[1] - allowed_area.top)
            to_left = abs(self.loc[0] - allowed_area.left)
            to_bottom = abs(self.loc[1] - allowed_area.bottom)
            to_right = abs(self.loc[0] - allowed_area.right)
            minimum = min(to_top, to_left, to_bottom, to_right)
            if to_top == minimum:
                self.angle = -2*math.pi - self.angle
                self.loc[1] = allowed_area.top
            elif to_left == minimum:
                self.angle = math.pi - self.angle
                self.loc[0] = allowed_area.left
            elif to_bottom == minimum:
                self.angle = -2*math.pi - self.angle
                self.loc[1] = allowed_area.bottom
            elif to_right == minimum:
                self.angle = math.pi - self.angle
                self.loc[0] = allowed_area.right
            self.angle += random.uniform(math.radians(-45), math.radians(45))
            self.last_collision = self.loc
            bounced = True
        else:
            if collide_rects is None:
                return
            for collide_rect in collide_rects:
                if collide_rect.collidepoint(self.loc):
                    to_top = abs(self.loc[1] - collide_rect.top)
                    to_left = abs(self.loc[0] - collide_rect.left)
                    to_bottom = abs(self.loc[1] - collide_rect.bottom)
                    to_right = abs(self.loc[0] - collide_rect.right)
                    minimum = min(to_top, to_left, to_bottom, to_right)
                    if to_top == minimum:
                        self.angle = -2*math.pi - self.angle
                        self.loc[1] = collide_rect.top
                    elif to_left == minimum:
                        self.angle = math.pi - self.angle
                        self.loc[0] = collide_rect.left
                    elif to_bottom == minimum:
                        self.angle = -2*math.pi - self.angle
                        self.loc[1] = collide_rect.bottom
                    elif to_right == minimum:
                        self.angle = math.pi - self.angle
                        self.loc[0] = collide_rect.right
            bounced = True
        if bounced:
            #Sound.play_sound_on_any_channel(Sound.spark)
            pass



    def move(self, delta_time: float, allowed_area: pg.Rect, collide_rects: Optional[List[pg.Rect]]):
        self.bounce_from_edge(allowed_area, collide_rects)
        distance = self.calculate_distance_to_move(delta_time)
        self.loc[0] += distance[0]
        self.loc[1] += distance[1]
        self.base_speed -= self.friction
        if self.base_speed <= 0:
            self.alive = False

        #angle_mod = 0.5; self.angle += random.uniform(-angle_mod / self.speed, angle_mod / self.speed)
        #self.point_towards(math.pi / 2, 0.02)
        #self.velocity_adjust(0.9, 0, 8, delta_time)
        #self.angle += 0.1


    # def velocity_adjust(self, friction: float, force: float, terminal_velocity: float, delta_time: float):
    #     movement = self.calculate_movement(delta_time)
    #     movement = (min(terminal_velocity, movement[1] + force * delta_time), movement[0] * friction)
    #     self.angle = math.atan2(movement[1], movement[0])


    # def point_towards(self, angle: float, rate: float) -> None:
    #     rotate_direction = ((angle - self.angle + math.pi * 3) % (math.pi * 2)) - math.pi
    #     try:
    #         rotate_sign = abs(rotate_direction) / rotate_direction
    #     except ZeroDivisionError:
    #         rotate_sign = 1
    #     if abs(rotate_direction) < rate:
    #         self.angle = angle
    #     else:
    #         self.angle += rate * rotate_sign


    def draw(self, screen_surface: pg.Surface):
        if self.alive:
            points = [
                [self.loc[0] + math.cos(self.angle) * self.base_speed * self.scale, self.loc[1] + math.sin(self.angle) * self.base_speed * self.scale],
                [self.loc[0] + math.cos(self.angle + math.pi / 2) * self.base_speed * self.scale * 0.3, self.loc[1] + math.sin(self.angle + math.pi / 2) * self.base_speed * self.scale * 0.3],
                [self.loc[0] - math.cos(self.angle) * self.base_speed * self.scale * 3.5, self.loc[1] - math.sin(self.angle) * self.base_speed * self.scale * 3.5],
                [self.loc[0] + math.cos(self.angle - math.pi / 2) * self.base_speed * self.scale * 0.3, self.loc[1] - math.sin(self.angle + math.pi / 2) * self.base_speed * self.scale * 0.3],
                ]
            pg.draw.polygon(screen_surface, self.color, points)

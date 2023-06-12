import math
import random
from typing import List, Optional, Tuple

import pygame as pg



class Spark:
    def __init__(
        self,
        loc: Tuple[int, int],
        angle: float,
        base_speed: float,
        friction: float,
        color: Tuple[int, int, int],
        scale: float = 1.0,
        speed_multiplier: float = 1.0,
    ):
        self.loc_x = loc[0]
        self.loc_y = loc[1]
        self.angle: float = angle
        self.base_speed: float = base_speed
        self.friction: float = friction
        self.scale: float = scale
        self.color: Tuple[int, int, int] = color
        self.alive: bool = True
        self.speed_multiplier: float = speed_multiplier

        self.last_collision: Tuple[int, int] = (self.loc_x, self.loc_y)

    def calculate_distance_to_move(self, delta_time: float) -> Tuple[float, float]:
        return (
            math.cos(self.angle) * self.speed_multiplier * self.base_speed * delta_time,
            math.sin(self.angle) * self.speed_multiplier * self.base_speed * delta_time,
        )

    def bounce_from_edge(self, allowed_area: pg.Rect, collide_rects: Optional[List[pg.Rect]]) -> None:
        if not allowed_area.collidepoint(self.loc_x, self.loc_y):
            to_top = abs(self.loc_y - allowed_area.top)
            to_left = abs(self.loc_x - allowed_area.left)
            to_bottom = abs(self.loc_y - allowed_area.bottom)
            to_right = abs(self.loc_x - allowed_area.right)
            minimum = min(to_top, to_left, to_bottom, to_right)
            if to_top == minimum:
                self.angle = -2 * math.pi - self.angle
                self.loc_y = allowed_area.top
            elif to_left == minimum:
                self.angle = math.pi - self.angle
                self.loc_x = allowed_area.left
            elif to_bottom == minimum:
                self.angle = -2 * math.pi - self.angle
                self.loc_y = allowed_area.bottom
            elif to_right == minimum:
                self.angle = math.pi - self.angle
                self.loc_x = allowed_area.right
            self.angle += random.uniform(math.radians(-45), math.radians(45))
            self.last_collision = (self.loc_x, self.loc_y)
        else:
            if collide_rects is None:
                return
            for collide_rect in collide_rects:
                if collide_rect.collidepoint((self.loc_x, self.loc_y)):
                    to_top = abs(self.loc_y - collide_rect.top)
                    to_left = abs(self.loc_x - collide_rect.left)
                    to_bottom = abs(self.loc_y - collide_rect.bottom)
                    to_right = abs(self.loc_x - collide_rect.right)
                    minimum = min(to_top, to_left, to_bottom, to_right)
                    if to_top == minimum:
                        self.angle = -2 * math.pi - self.angle
                        self.loc_y = collide_rect.top
                    elif to_left == minimum:
                        self.angle = math.pi - self.angle
                        self.loc_x = collide_rect.left
                    elif to_bottom == minimum:
                        self.angle = -2 * math.pi - self.angle
                        self.loc_y = collide_rect.bottom
                    elif to_right == minimum:
                        self.angle = math.pi - self.angle
                        self.loc_x = collide_rect.right

    def move(self, delta_time: float, allowed_area: pg.Rect, collide_rects: Optional[List[pg.Rect]]):
        self.bounce_from_edge(allowed_area, collide_rects)
        distance = self.calculate_distance_to_move(delta_time)
        self.loc_x += distance[0]
        self.loc_y += distance[1]
        self.base_speed -= self.friction
        if self.base_speed <= 0:
            self.alive = False

    def draw(self, screen_surface: pg.Surface):
        if self.alive:
            points = [
                [
                    self.loc_x + math.cos(self.angle) * self.base_speed * self.scale,
                    self.loc_y + math.sin(self.angle) * self.base_speed * self.scale,
                ],
                [
                    self.loc_x + math.cos(self.angle + math.pi / 2) * self.base_speed * self.scale * 0.3,
                    self.loc_y + math.sin(self.angle + math.pi / 2) * self.base_speed * self.scale * 0.3,
                ],
                [
                    self.loc_x - math.cos(self.angle) * self.base_speed * self.scale * 3.5,
                    self.loc_y - math.sin(self.angle) * self.base_speed * self.scale * 3.5,
                ],
                [
                    self.loc_x + math.cos(self.angle - math.pi / 2) * self.base_speed * self.scale * 0.3,
                    self.loc_y - math.sin(self.angle + math.pi / 2) * self.base_speed * self.scale * 0.3,
                ],
            ]
            pg.draw.polygon(screen_surface, self.color, points)



class SparkStyle:
    def __init__(self, colors: List[Tuple[int, int, int]]) -> None:
        self.colors: List[Tuple[int, int, int]] = colors



class FlameSparkStyle(SparkStyle):
    def __init__(self) -> None:
        super().__init__(
            colors = [
                (255, 207, 119), (254, 126, 5), (239, 99, 5), (177, 72, 3), (255, 237, 168)
            ]
        )

class WeldingSparkStyle(SparkStyle):
    def __init__(self) -> None:
        super().__init__(
            colors = [
                (255, 255, 255), (126, 205, 210), (252, 192, 46), (201, 230, 234), (236, 197, 104)
            ]
        )


class SparkBehavior:
    def __init__(self, speed: float, speed_deviation: float, friction: float, friction_deviation: float, scale: float, speed_multiplier: float) -> None:
        self.speed_min: float = speed - speed_deviation
        self.speed_max: float = speed + speed_deviation
        self.friction_min: float = friction - friction_deviation
        self.friction_max: float = friction + friction_deviation
        self.scale: float = scale
        self.speed_multiplier: float = speed_multiplier


class SlowLargeSpark(SparkBehavior):
    def __init__(self) -> None:
        super().__init__(
            speed = 2.5,
            speed_deviation = 0.5,
            friction = 0.02,
            friction_deviation= 0.01,
            scale = 5.0,
            speed_multiplier = 0.5,
        )


class FastSmallSpark(SparkBehavior):
    def __init__(self) -> None:
        super().__init__(
            speed = 0.5,
            speed_deviation = 0.25,
            friction = 0.01,
            friction_deviation = 0.005,
            scale = 5.0,
            speed_multiplier=5.0
        )


class FastSmallShortLivedSpark(SparkBehavior):
    def __init__(self) -> None:
        super().__init__(
            speed = 0.75,
            speed_deviation = 0.25,
            friction = 0.04,
            friction_deviation = 0.005,
            scale = 5.0,
            speed_multiplier=5.0
        )



class CloudShape:
    def __init__(self, angle: float, angle_deviation: float) -> None:
        self.angle_min = -int(angle - angle_deviation)
        self.angle_max = -int(angle + angle_deviation)


class CircleCloudShape(CloudShape):
    def __init__(self, angle) -> None:
        super().__init__(
            angle = angle,
            angle_deviation = 180
        )


class WideConeCloudShape(CloudShape):
    def __init__(self, angle: float) -> None:
        super().__init__(
            angle = angle,
            angle_deviation = 70
        )


class NarrowConeCloudShape(CloudShape):
    def __init__(self, angle: float) -> None:
        super().__init__(
            angle = angle,
            angle_deviation = 20
        )


class SparkCloud:
    def __init__(self, pos: Tuple[int, int], shape: CloudShape, pos_deviation: Tuple[int, int] = (0, 0), style: SparkStyle = FlameSparkStyle(), behavior: SparkBehavior = SlowLargeSpark(), spark_count: int = 10, spark_count_deviation: int = 0) -> None:
        self.pos: Tuple[int, int] = pos
        self.pos_deviation: Tuple[int, int] = pos_deviation
        self.shape: CloudShape = shape
        self.style: SparkStyle = style
        self.spark_count: int = spark_count
        self.spark_count_deviation: int = spark_count_deviation
        self.behavior: SparkBehavior = behavior

    def emit_sparks(self) -> List[Spark]:
        spark_list: List[Spark] = []
        sparks_to_create = self.spark_count + random.randint(-int(self.spark_count_deviation / 2), int(self.spark_count_deviation / 2))
        for _ in range(sparks_to_create):
            spark_list.append(
                Spark(
                    loc=(self.pos[0] + random.randint(-self.pos_deviation[0], self.pos_deviation[0]), self.pos[1] + random.randint(-self.pos_deviation[1], self.pos_deviation[1])),
                    angle=math.radians(random.uniform(self.shape.angle_min, self.shape.angle_max)),
                    base_speed=random.uniform(self.behavior.speed_min, self.behavior.speed_max),
                    friction=random.uniform(self.behavior.friction_min, self.behavior.friction_max),
                    color=random.sample(self.style.colors, 1)[0],
                    scale=self.behavior.scale,
                    speed_multiplier=self.behavior.speed_multiplier,
                )
            )
        return spark_list

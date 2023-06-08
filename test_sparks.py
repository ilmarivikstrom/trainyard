import math
import random
import sys
import pygame as pg
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from src.spark import Spark

clock = pg.time.Clock()

pg.init()
pg.display.set_caption('game base')
screen_surface = pg.display.set_mode((500, 500), 0, 32)

sparks = []

collide_rects = [
#    pg.Rect(100, 100, 100, 100),
#    pg.Rect(300, 300, 100, 100),
]
allowed_area = pg.Rect(50, 50, 400, 400)

iteration = 0

while True:
    screen_surface.fill((0,0,0))

    for i, spark in sorted(enumerate(sparks), reverse=True):
        spark.move(1, allowed_area, collide_rects)
        spark.draw(screen_surface)
        if not spark.alive:
            sparks.pop(i)

    mx, my = pg.mouse.get_pos()

    spark_colors = [
        (255, 207, 119),
        (254, 126, 5),
        (239, 99, 5),
        (177, 72, 3),
        (255, 237, 168)
    ]

    if iteration < 1:
        for i in range(100):
            sparks.append(
                Spark(
                    loc=[mx + random.randint(0, 20) - 10, my + random.randint(0, 20) - 10],
                    angle=math.radians(random.randint(0, 360)),
                    #speed=random.uniform(1, 10),
                    base_speed=random.choices([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [0.2, 0.2, 0.2, 0.2, 0.1, 0.05, 0.02, 0.01, 0.01, 0.01])[0],
                    #friction=0.2,
                    friction=random.uniform(0.15, 0.25),
                    color=random.sample(spark_colors, 1)[0],
                    scale=1.0,
                    speed_multiplier=1.0
                )
            )

    iteration += 1
    if iteration % 50 == 0:
        iteration = 0

    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pg.quit()
                sys.exit()

    pg.display.update()
    clock.tick(60)

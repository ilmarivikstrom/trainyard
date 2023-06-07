import math
import random
import sys
import pygame as pg
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from src.spark import Spark

clock = pg.time.Clock()

pg.init()
pg.display.set_caption('game base')
screen = pg.display.set_mode((500, 500), 0, 32)

sparks = []

collide_rects = [
#    pg.Rect(100, 100, 100, 100),
#    pg.Rect(300, 300, 100, 100),
]
allowed_area = pg.Rect(50, 50, 400, 400)

iteration = 0

while True:
    screen.fill((0,0,0))

    for i, spark in sorted(enumerate(sparks), reverse=True):
        spark.move(1, allowed_area, collide_rects)
        spark.draw(screen)
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

    if iteration < 10:
        for i in range(20):
            sparks.append(Spark([mx + random.randint(0, 20) - 10, my + random.randint(0, 20) - 10], math.radians(random.randint(0, 360)), random.uniform(1, 5), random.sample(spark_colors, 1)[0], 1.0))

    if iteration % 50 == 0:
        iteration = 0
    iteration += 1

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

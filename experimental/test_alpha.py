import pygame as pg

clock = pg.time.Clock()

pg.init()

screen = pg.display.set_mode((800, 600), 0, 32)

surface1 = pg.Surface((100, 100))
surface1.set_colorkey((0, 0, 0))
surface1.set_alpha(255)
surface2 = pg.Surface((100, 100))
surface2.set_colorkey((0, 0, 0))
surface2.set_alpha(255)


def dim_surface(surface: pg.Surface, dim_speed: int) -> None:
    surface.set_alpha(surface.get_alpha() - dim_speed)
    return surface


while True:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()

    surface1 = dim_surface(surface1, dim_speed=7)
    surface2 = dim_surface(surface2, dim_speed=7)

    pg.draw.circle(surface1, (0, 255, 0), (50, 50), 50)
    pg.draw.circle(surface2, (255, 0, 0), (50, 50), 50)

    screen.blit(surface1, (100, 100))
    screen.blit(surface2, (120, 120))

    pg.display.update()
    clock.tick(60)

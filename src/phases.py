import math
import sys

import pygame as pg
from pygame.locals import QUIT

from src.color_constants import *
from src.controls import UserControl
from src.field import Field, TrackType
from src.game_context import Ctx, Direction, Phase, Resources
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")


def main_menu_phase() -> None:
    Ctx.screen_surface.fill((10, 10, 10))
    check_quit_event()
    pressed_keys = pg.key.get_pressed()
    if pressed_keys[UserControl.GAMEPLAY]:
        Ctx.game_phase = Phase.GAMEPLAY
        logger.info(f"Moving to state {Ctx.game_phase}")
    elif pressed_keys[UserControl.EXIT]:
        Ctx.game_phase = Phase.GAME_END
        logger.info(f"Moving to state {Ctx.game_phase}")


def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pg.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def gameplay_phase() -> None:
    check_quit_event()
    Ctx.update_gameplay_state()

    # Check if delete mode, change background color accordingly.
    if Ctx.delete_mode:
        Ctx.screen_surface.fill(DELETE_MODE_BG_COLOR)
    else:
        Ctx.screen_surface.fill(NORMAL_MODE_BG_COLOR)

    Ctx.cell_sprites.draw(Ctx.screen_surface)

    Ctx.train.on_track = False
    Ctx.train.at_endpoint = False

    # Iterate over all the cells on the map.
    for (_, cell) in enumerate(Field.grid):

        # 2. Draw track images on top of the cells.
        for (_, track) in enumerate(cell.tracks):
            for endpoint in track.endpoints:
                if Ctx.train.rect.center == endpoint:
                    Ctx.train.at_endpoint = True
            track.draw()

        # TODO: Check if train is on the track, how to proceed then?
        # TODO: Why is there a 1 pixel shift every corner?
        if cell.rect.colliderect(pg.Rect(Ctx.train.rect.centerx - 1, Ctx.train.rect.centery - 1, 2, 2)):
            for track in cell.tracks:
                Ctx.train.on_track = True
                if track.track_type == TrackType.vert:
                    if Ctx.train.direction == Direction.UP:
                        Ctx.train.velocity.x = 0
                        Ctx.train.velocity.y = -1
                        Ctx.train.direction = Direction.UP
                    elif Ctx.train.direction == Direction.DOWN:
                        Ctx.train.velocity.x = 0
                        Ctx.train.velocity.y = 1
                        Ctx.train.direction = Direction.DOWN
                elif track.track_type == TrackType.hori:
                    if Ctx.train.direction == Direction.RIGHT:
                        Ctx.train.velocity.x = 1
                        Ctx.train.velocity.y = 0
                        Ctx.train.direction = Direction.RIGHT
                    elif Ctx.train.direction == Direction.LEFT:
                        Ctx.train.velocity.x = -1
                        Ctx.train.velocity.y = 0
                        Ctx.train.direction = Direction.LEFT
                elif track.track_type == TrackType.topright:
                    if Ctx.train.direction == Direction.LEFT:
                        Ctx.train.velocity.x = -1 * math.sqrt(2) / 2
                        Ctx.train.velocity.y = -1 * math.sqrt(2) / 2
                        Ctx.train.direction = Direction.UP
                    elif Ctx.train.direction == Direction.DOWN:
                        Ctx.train.velocity.x = 1 * math.sqrt(2) / 2
                        Ctx.train.velocity.y = 1 * math.sqrt(2) / 2
                        Ctx.train.direction = Direction.RIGHT
                elif track.track_type == TrackType.topleft:
                    if Ctx.train.direction == Direction.RIGHT:
                        Ctx.train.velocity.x = 1 * math.sqrt(2) / 2
                        Ctx.train.velocity.y = -1 * math.sqrt(2) / 2
                        Ctx.train.direction = Direction.UP
                    elif Ctx.train.direction == Direction.DOWN:
                        Ctx.train.velocity.x = -1 * math.sqrt(2) / 2
                        Ctx.train.velocity.y = 1 * math.sqrt(2) / 2
                        Ctx.train.direction = Direction.LEFT
                elif track.track_type == TrackType.bottomleft:
                    if Ctx.train.direction == Direction.RIGHT:
                        Ctx.train.velocity.x = 1 * math.sqrt(2) / 2
                        Ctx.train.velocity.y = 1 * math.sqrt(2) / 2
                        Ctx.train.direction = Direction.DOWN
                    elif Ctx.train.direction == Direction.UP:
                        Ctx.train.velocity.x = -1 * math.sqrt(2) / 2
                        Ctx.train.velocity.y = -1 * math.sqrt(2) / 2
                        Ctx.train.direction = Direction.LEFT
                elif track.track_type == TrackType.bottomright:
                    if Ctx.train.direction == Direction.LEFT:
                        Ctx.train.velocity.x = -1 * math.sqrt(2) / 2
                        Ctx.train.velocity.y = 1 * math.sqrt(2) / 2
                        Ctx.train.direction = Direction.DOWN
                    elif Ctx.train.direction == Direction.UP:
                        Ctx.train.velocity.x = 1 * math.sqrt(2) / 2
                        Ctx.train.velocity.y = -1 * math.sqrt(2) / 2
                        Ctx.train.direction = Direction.RIGHT


        # 3. If mouse not on rect, continue the for loop.
        if not cell.rect.collidepoint(Ctx.mouse_pos):
            if cell.mouse_on:
                cell.mouse_exit()
            continue

        # 4. If mouse is on the rect.
        cell.mouse_enter()
        if Ctx.mouse_pressed[0] == True:
            if Ctx.delete_mode:
                cell.tracks.clear()
    
    Ctx.update_trains()

    Ctx.train_sprites.draw(Ctx.screen_surface)

    # Place track on the cell based on the mouse movements.
    if Ctx.mouse_pressed[0] and not Ctx.delete_mode and Ctx.prev_cell_needs_checking:
        if Ctx.prev_cell is not None and Ctx.curr_cell is not None:
            if (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.UP) or (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackType.vert, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.LEFT):
                Field.place_track_item(TrackType.hori, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.LEFT) or (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackType.bottomleft, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackType.bottomright, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.UP):
                Field.place_track_item(TrackType.topright, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.LEFT) or (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.UP):
                Field.place_track_item(TrackType.topleft, Ctx.prev_cell)
    

    # Back to main menu.
    if Ctx.pressed_keys[UserControl.MAIN_MENU]:
        Ctx.game_phase = Phase.MAIN_MENU
        logger.info(f"Moving to state {Ctx.game_phase}")


def exit_phase():
    logger.info("Exiting game...")
    pg.quit()
    sys.exit()


def check_quit_event() -> None:
    for event in pg.event.get():
        if event.type == QUIT:
            Ctx.game_phase = Phase.GAME_END
            logger.info(f"Moving to state {Ctx.game_phase}")
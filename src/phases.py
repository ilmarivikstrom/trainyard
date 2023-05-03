import sys
from math import sqrt

import pygame as pg
from pygame.locals import QUIT

from src.color_constants import *
from src.controls import UserControl
from src.field import Field, TrackType, place_track_item
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


def gameplay_phase() -> None:
    check_quit_event()
    Ctx.update_gameplay_state()

    # Check if delete mode, change background color accordingly.
    if Ctx.delete_mode:
        Ctx.screen_surface.fill(DELETE_MODE_BG_COLOR)
    else:
        Ctx.screen_surface.fill(NORMAL_MODE_BG_COLOR)

    Ctx.cell_sprites.draw(Ctx.screen_surface)

    # Iterate over all the cells on the map.
    for (_, cell) in enumerate(Field.grid):

        # 2. Draw track images on top of the cells.
        for (_, track) in enumerate(cell.tracks):
            track.draw()

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
    
    # Stop the train if not on track cell.
    if not Ctx.train.on_track:
        Ctx.train.velocity.x = 0
        Ctx.train.velocity.y = 0

    Ctx.update_trains()

    # 5. Draw the trains.
    train_variant = "train0"
    if Ctx.train.direction == Direction.RIGHT:
        train_variant = "train0"
    elif Ctx.train.direction == Direction.UP:
        train_variant = "train90"
    elif Ctx.train.direction == Direction.LEFT:
        train_variant = "train180"
    elif Ctx.train.direction == Direction.DOWN:
        train_variant = "train270"
    Ctx.train.image = Resources.train_surfaces[train_variant]

    Ctx.train_sprites.draw(Ctx.screen_surface)

    # Place track on the cell based on the mouse movements.
    if Ctx.mouse_pressed[0] and not Ctx.delete_mode and Ctx.prev_cell_needs_checking:
        if Ctx.prev_cell is not None and Ctx.curr_cell is not None:
            if (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.UP) or (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.DOWN):
                place_track_item(TrackType.vert, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.LEFT):
                place_track_item(TrackType.hori, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.LEFT) or (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.DOWN):
                place_track_item(TrackType.bottomleft, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.DOWN):
                place_track_item(TrackType.bottomright, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.UP):
                place_track_item(TrackType.topright, Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.LEFT) or (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.UP):
                place_track_item(TrackType.topleft, Ctx.prev_cell)
    

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
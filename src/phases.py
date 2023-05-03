from math import sqrt
import sys
import pygame as pg
from pygame.locals import QUIT
from src.controls import UserControl
from src.game_context import Phase, Ctx, Direction, Resources
from src.utils import setup_logging
from src.field import Field
from src.color_constants import *
from src.field import TrackItem

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


    Ctx.train_on_track = False

    # Iterate over all the cells on the map.
    for (cell_index, cell) in enumerate(Field.grid):
        # 1. Draw background rects.
        pg.draw.rect(
            surface=Ctx.screen_surface,
            color=cell.color,
            rect=cell.base_rect,
            width=cell.line_width,
        )

        # 2. Draw track images on top of the cells.
        for (index, track_item) in enumerate(cell.track_items):
            # TODO: Instead, set some cell track level value to "active" / "inactive", toggled, or so.
            # TODO: Handle the case where there is no overlap, eg. "c0 c180"
            if len(cell.track_items) > 1 and index == 0:
                track_item.surface.set_alpha(100)
            else:
                track_item.surface.set_alpha(255)
            Ctx.screen_surface.blit(track_item.surface, (cell.base_rect.x, cell.base_rect.y))

            # Move the train according to the track.
            #if cell.base_rect.collidepoint(Ctx.train_pos + (32, 32)):
            if cell.base_rect.colliderect(pg.Rect(Ctx.train_pos.x + 31, Ctx.train_pos.y + 31, 2, 2)):
                Ctx.train_on_track = True
                if all(direction in track_item.directions for direction in [Direction.UP, Direction.DOWN]):
                    if Ctx.train_dir == Direction.UP:
                        Ctx.train_vel.x = 0
                        Ctx.train_vel.y = -1
                    elif Ctx.train_dir == Direction.DOWN:
                        Ctx.train_vel.x = 0
                        Ctx.train_vel.y = 1
                elif all(direction in track_item.directions for direction in [Direction.RIGHT, Direction.LEFT]):
                    if Ctx.train_dir == Direction.RIGHT:
                        Ctx.train_vel.x = 1
                        Ctx.train_vel.y = 0
                    elif Ctx.train_dir == Direction.LEFT:
                        Ctx.train_vel.x = -1
                        Ctx.train_vel.y = 0
                elif all(direction in track_item.directions for direction in [Direction.RIGHT, Direction.UP]):
                    if Ctx.train_dir == Direction.LEFT:
                        Ctx.train_vel.x = -sqrt(2)/2
                        Ctx.train_vel.y = -sqrt(2)/2
                        Ctx.train_dir = Direction.UP
                    elif Ctx.train_dir == Direction.DOWN:
                        Ctx.train_vel.x = sqrt(2)/2
                        Ctx.train_vel.y = sqrt(2)/2
                        Ctx.train_dir = Direction.RIGHT
                elif all(direction in track_item.directions for direction in [Direction.UP, Direction.LEFT]):
                    if Ctx.train_dir == Direction.RIGHT:
                        Ctx.train_vel.x = sqrt(2)/2
                        Ctx.train_vel.y = -sqrt(2)/2
                        Ctx.train_dir = Direction.UP
                    elif Ctx.train_dir == Direction.DOWN:
                        Ctx.train_vel.x = -sqrt(2)/2
                        Ctx.train_vel.y = sqrt(2)/2
                        Ctx.train_dir = Direction.LEFT
                elif all(direction in track_item.directions for direction in [Direction.LEFT, Direction.DOWN]):
                    if Ctx.train_dir == Direction.RIGHT:
                        Ctx.train_vel.x = sqrt(2)/2
                        Ctx.train_vel.y = sqrt(2)/2
                        Ctx.train_dir = Direction.DOWN
                    elif Ctx.train_dir == Direction.UP:
                        Ctx.train_vel.x = -sqrt(2)/2
                        Ctx.train_vel.y = -sqrt(2)/2
                        Ctx.train_dir = Direction.LEFT
                elif all(direction in track_item.directions for direction in [Direction.RIGHT, Direction.DOWN]):
                    if Ctx.train_dir == Direction.LEFT:
                        Ctx.train_vel.x = -sqrt(2)/2
                        Ctx.train_vel.y = sqrt(2)/2
                        Ctx.train_dir = Direction.DOWN
                    elif Ctx.train_dir == Direction.UP:
                        Ctx.train_vel.x = sqrt(2)/2
                        Ctx.train_vel.y = -sqrt(2)/2
                        Ctx.train_dir = Direction.RIGHT

        SPEED_MODIFIER = 1
        if Ctx.train_vel.length() > 1:
            Ctx.train_vel = Ctx.train_vel.normalize()
        Ctx.train_vel *= SPEED_MODIFIER

        # 3. If mouse not on rect, continue the for loop.
        if not cell.base_rect.collidepoint(Ctx.mouse_pos):
            if cell.mouse_on:
                cell.mouse_exit()
            continue

        # 4. If mouse is on the rect.
        cell.mouse_enter()
        if Ctx.mouse_pressed[0] == True:
            if Ctx.delete_mode:
                cell.track_items = []
    
    # Stop the train if not on track cell.
    if not Ctx.train_on_track:
        Ctx.train_vel.x = 0
        Ctx.train_vel.y = 0

    Ctx.update_trains()

    # 5. Draw the trains.
    train_variant = "train0"
    if Ctx.train_dir == Direction.RIGHT:
        train_variant = "train0"
    elif Ctx.train_dir == Direction.UP:
        train_variant = "train90"
    elif Ctx.train_dir == Direction.LEFT:
        train_variant = "train180"
    elif Ctx.train_dir == Direction.DOWN:
        train_variant = "train270"
    Ctx.screen_surface.blit(Resources.train_surfaces[train_variant], Ctx.train_pos)

    # Place track on the cell based on the mouse movements.
    if Ctx.mouse_pressed[0] and not Ctx.delete_mode and Ctx.prev_cell_needs_checking:
        if Ctx.prev_cell is not None and Ctx.curr_cell is not None:
            if (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.UP) or (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackItem("s90"), Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.LEFT):
                Field.place_track_item(TrackItem("s0"), Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.LEFT) or (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackItem("c0"), Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.UP and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackItem("c90"), Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.RIGHT) or (Ctx.prev_movement == Direction.LEFT and Ctx.curr_movement == Direction.UP):
                Field.place_track_item(TrackItem("c180"), Ctx.prev_cell)
            elif (Ctx.prev_movement == Direction.DOWN and Ctx.curr_movement == Direction.LEFT) or (Ctx.prev_movement == Direction.RIGHT and Ctx.curr_movement == Direction.UP):
                Field.place_track_item(TrackItem("c270"), Ctx.prev_cell)

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
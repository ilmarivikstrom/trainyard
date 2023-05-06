import math
import sys

import pygame as pg
from pygame.locals import QUIT

from src.color_constants import DELETE_MODE_BG_COLOR, NORMAL_MODE_BG_COLOR
from src.controls import UserControl
from src.field import Field, TrackType
from src.game_state import State, Direction, Phase
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")


def main_menu_phase() -> None:
    State.screen_surface.fill((10, 10, 10))
    check_events()
    pressed_keys = pg.key.get_pressed()
    if pressed_keys[UserControl.GAMEPLAY]:
        State.game_phase = Phase.GAMEPLAY
        logger.info(f"Moving to state {State.game_phase}")
    elif pressed_keys[UserControl.EXIT]:
        State.game_phase = Phase.GAME_END
        logger.info(f"Moving to state {State.game_phase}")


def gameplay_phase() -> None:
    check_events()
    State.update_gameplay_state()

    # Check if delete mode, change background color accordingly.
    if State.delete_mode:
        State.screen_surface.fill(DELETE_MODE_BG_COLOR)
    else:
        State.screen_surface.fill(NORMAL_MODE_BG_COLOR)

    State.cell_sprites.draw(State.screen_surface)

    State.train.on_track = False
    State.train.at_endpoint = False

    # Iterate over all the cells on the map.
    for (_, cell) in enumerate(Field.grid):

        # 2. Draw track images on top of the cells.
        for (_, track) in enumerate(cell.tracks):
            for endpoint in track.endpoints:
                if State.train.rect.center == endpoint:
                    State.train.at_endpoint = True
            track.draw()

        if cell.rect.colliderect(pg.Rect(State.train.rect.centerx - 1, State.train.rect.centery - 1, 1, 1)):
            if cell not in State.train.last_collided_cells or State.train.selected_track is None:
                if len(cell.tracks) == 0:
                    State.train.on_track = False
                    State.train.selected_track = None
                else:
                    State.train.tracks_ahead = cell.tracks
                    possible_tracks = []
                    if len(State.train.tracks_ahead) > 0:
                        for track_ahead in cell.tracks:
                            for endpoint in track_ahead.endpoints:
                                if State.train.rect.collidepoint(endpoint):
                                    possible_tracks.append(track_ahead)
                        if len(possible_tracks) > 0:
                            if len(possible_tracks) == 1:
                                State.train.selected_track = possible_tracks[0]
                            elif len(possible_tracks) == 2:
                                for possible_track in possible_tracks:
                                    if possible_track.bright:
                                        State.train.selected_track = possible_track
                            print(f"Selected track: {State.train.selected_track.directions}")
                        else:
                            State.train.on_track = False
                            State.train.selected_track = None
                            print("No track to be selected. Train is not on track.")
                State.train.last_collided_cells.append(cell)
                State.train.last_collided_cells = State.train.last_collided_cells[-2:]
            if cell.rect.contains(State.train.rect) and State.train.last_flipped_cell != cell:
                if len(cell.tracks) > 1:
                    cell.flip_tracks()
                    State.train.last_flipped_cell = cell
            if State.train.selected_track is not None:
                for track in [State.train.selected_track]:
                    State.train.on_track = True
                    if track.track_type == TrackType.VERT:
                        if State.train.direction == Direction.UP:
                            State.train.angle = math.radians(90)
                        elif State.train.direction == Direction.DOWN:
                            State.train.angle = math.radians(270)
                    elif track.track_type == TrackType.HORI:
                        if State.train.direction == Direction.RIGHT:
                            State.train.angle = math.radians(0)
                        elif State.train.direction == Direction.LEFT:
                            State.train.angle = math.radians(180)
                    elif track.track_type == TrackType.TOP_RIGHT:
                        if State.train.direction == Direction.LEFT:
                            State.train.angle -= State.angular_vel
                            if State.train.angle <= math.radians(90) + 2 * State.angular_vel:
                                State.train.direction = Direction.UP
                                State.train.angle = math.radians(90)
                        elif State.train.direction == Direction.DOWN:
                            State.train.angle += State.angular_vel
                            if State.train.angle >= math.radians(360) - 2 * State.angular_vel:
                                State.train.direction = Direction.RIGHT
                                State.train.angle = math.radians(0)
                    elif track.track_type == TrackType.TOP_LEFT:
                        if State.train.direction == Direction.RIGHT:
                            State.train.angle += State.angular_vel
                            if State.train.angle >= math.radians(90) - 2 * State.angular_vel:
                                State.train.direction = Direction.UP
                                State.train.angle = math.radians(90)
                        elif State.train.direction == Direction.DOWN:
                            State.train.angle -= State.angular_vel
                            if State.train.angle <= math.radians(180) + 2 * State.angular_vel:
                                State.train.direction = Direction.LEFT
                                State.train.angle = math.radians(180)
                    elif track.track_type == TrackType.BOTTOM_LEFT:
                        if State.train.direction == Direction.RIGHT:
                            State.train.angle -= State.angular_vel
                            if State.train.angle <= math.radians(-90) + 2 * State.angular_vel:
                                State.train.direction = Direction.DOWN
                                State.train.angle = math.radians(270)
                        elif State.train.direction == Direction.UP:
                            State.train.angle += State.angular_vel
                            if State.train.angle >= math.radians(180) - 2 * State.angular_vel:
                                State.train.direction = Direction.LEFT
                                State.train.angle = math.radians(180)
                    elif track.track_type == TrackType.BOTTOM_RIGHT:
                        if State.train.direction == Direction.LEFT:
                            State.train.angle += State.angular_vel
                            if State.train.angle >= math.radians(270) - 2 * State.angular_vel:
                                State.train.direction = Direction.DOWN
                                State.train.angle = math.radians(270)
                        elif State.train.direction == Direction.UP:
                            State.train.angle -= State.angular_vel
                            if State.train.angle <= math.radians(0) + 2 * State.angular_vel:
                                State.train.direction = Direction.RIGHT
                                State.train.angle = math.radians(0)

        # 3. If mouse not on rect, continue the for loop.
        if not cell.rect.collidepoint(State.mouse_pos):
            if cell.mouse_on:
                cell.mouse_exit()
            continue

        # 4. If mouse is on the rect.
        cell.mouse_enter()
        if State.mouse_pressed[0] == True:
            if State.delete_mode:
                cell.tracks.clear()
    
    State.train.update()

    State.train_sprites.draw(State.screen_surface)

    # Place track on the cell based on the mouse movements.
    if State.mouse_pressed[0] and not State.delete_mode and State.prev_cell_needs_checking:
        if State.prev_cell is not None and State.curr_cell is not None:
            if (State.prev_movement == Direction.UP and State.curr_movement == Direction.UP) or (State.prev_movement == Direction.DOWN and State.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackType.VERT, State.prev_cell)
            elif (State.prev_movement == Direction.RIGHT and State.curr_movement == Direction.RIGHT) or (State.prev_movement == Direction.LEFT and State.curr_movement == Direction.LEFT):
                Field.place_track_item(TrackType.HORI, State.prev_cell)
            elif (State.prev_movement == Direction.UP and State.curr_movement == Direction.LEFT) or (State.prev_movement == Direction.RIGHT and State.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackType.BOTTOM_LEFT, State.prev_cell)
            elif (State.prev_movement == Direction.UP and State.curr_movement == Direction.RIGHT) or (State.prev_movement == Direction.LEFT and State.curr_movement == Direction.DOWN):
                Field.place_track_item(TrackType.BOTTOM_RIGHT, State.prev_cell)
            elif (State.prev_movement == Direction.DOWN and State.curr_movement == Direction.RIGHT) or (State.prev_movement == Direction.LEFT and State.curr_movement == Direction.UP):
                Field.place_track_item(TrackType.TOP_RIGHT, State.prev_cell)
            elif (State.prev_movement == Direction.DOWN and State.curr_movement == Direction.LEFT) or (State.prev_movement == Direction.RIGHT and State.curr_movement == Direction.UP):
                Field.place_track_item(TrackType.TOP_LEFT, State.prev_cell)

    # Back to main menu.
    if State.pressed_keys[UserControl.MAIN_MENU]:
        State.game_phase = Phase.MAIN_MENU
        logger.info(f"Moving to state {State.game_phase}")


def exit_phase():
    logger.info("Exiting game...")
    pg.quit()
    sys.exit()


def check_events() -> None:
    for event in pg.event.get():
        if event.type == QUIT:
            State.game_phase = Phase.GAME_END
            logger.info(f"Moving to state {State.game_phase}")
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                for cell in Field.grid:
                    if cell.mouse_on:
                        cell.flip_tracks()

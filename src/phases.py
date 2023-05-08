import math
import sys

import pygame as pg
from pygame.locals import QUIT

from src.color_constants import DELETE_MODE_BG_COLOR, NORMAL_MODE_BG_COLOR, GRAY10
from src.controls import UserControl
from src.field import Field, TrackType
from src.game_state import State, Direction, Phase
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")


def main_menu_phase() -> None:
    State.screen_surface.fill(GRAY10)
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

    # 1. Draw cell sprites.
    State.cell_sprites.draw(State.screen_surface)

    for train in State.trains:
        train.on_track = False
        train.at_endpoint = False

    # Iterate over all the cells on the map.
    for (_, cell) in enumerate(Field.grid):

        # 2. Draw track sprites on top of the cells.
        for (_, track) in enumerate(cell.tracks):
            for endpoint in track.endpoints:
                for train in State.trains:
                    if train.rect.center == endpoint:
                        train.at_endpoint = True
            track.draw()

        # If train 'release' command has been given.
        if State.train_go:
            for train in State.trains:
                # If the cell in question intersects with the center of the train.
                if cell.rect.colliderect(pg.Rect(train.rect.centerx - 1, train.rect.centery - 1, 1, 1)):
                    # If this is a new cell OR there is no info about the selected track.
                    if cell not in train.last_collided_cells or train.selected_track is None:
                        # Add the cell to the last collided cells.
                        train.last_collided_cells.append(cell)
                        train.last_collided_cells = train.last_collided_cells[-2:]
                        # Reset the last flipped cell.
                        train.last_flipped_cell = None
                        # If there are no tracks in this cell.
                        if len(cell.tracks) == 0:
                            # Stop the train. Should mean 'crash'.
                            train.on_track = False
                            train.selected_track = None
                        else:
                            # If there are some tracks in this cell.
                            train.tracks_ahead = cell.tracks
                            possible_tracks = []
                            # If the state has just been reset, select the only available track.
                            if train.is_reset:
                                possible_tracks.append(cell.tracks[0])
                            else:
                                # Let's find all tracks in this cell that have an endpoint where the train is.
                                for track_ahead in cell.tracks:
                                    for endpoint in track_ahead.endpoints:
                                        if train.rect.collidepoint(endpoint):
                                            possible_tracks.append(track_ahead)
                            if len(possible_tracks) > 0:
                                # If there is only 1 possible track, select that.
                                if len(possible_tracks) == 1:
                                    train.selected_track = possible_tracks[0]
                                elif len(possible_tracks) == 2:
                                    # If there are more possible tracks, select the one that is 'bright'.
                                    for possible_track in possible_tracks:
                                        if possible_track.bright:
                                            train.selected_track = possible_track
                                print(f"Selected track: {train.selected_track.directions}")
                            else:
                                # If there are no possible tracks available. Should 'crash'.
                                train.on_track = False
                                train.selected_track = None
                                print("No track to be selected. Train is not on track.")
                    # If the cell wholly contains the train, and the last flipped cell was some other cell.
                    if cell.rect.contains(train.rect) and train.last_flipped_cell != cell:
                        # If there are 2 tracks, flip them now. TOOD: Should only flip if they intersect.
                        if len(cell.tracks) == 2:
                            cell.flip_tracks()
                            train.last_flipped_cell = cell


                    # If the train has selected a track.
                    if train.selected_track is not None:
                        train.on_track = True
                        # If the selected track is vertical.
                        if train.selected_track.track_type == TrackType.VERT:
                            if train.direction == Direction.UP:
                                train.angle = math.radians(90)
                            elif train.direction == Direction.DOWN:
                                train.angle = math.radians(270)
                        # If the selected track is horizontal.
                        elif train.selected_track.track_type == TrackType.HORI:
                            if train.direction == Direction.RIGHT:
                                train.angle = math.radians(0)
                            elif train.direction == Direction.LEFT:
                                train.angle = math.radians(180)
                        # If the selected track is top-right.
                        elif train.selected_track.track_type == TrackType.TOP_RIGHT:
                            if train.direction == Direction.LEFT:
                                train.angle -= State.angular_vel
                                if train.angle <= math.radians(90) + 0.5 * State.angular_vel:
                                    train.direction = Direction.UP
                                    train.angle = math.radians(90)
                            elif train.direction == Direction.DOWN:
                                train.angle += State.angular_vel
                                if train.angle >= math.radians(360) - 0.5 * State.angular_vel:
                                    train.direction = Direction.RIGHT
                                    train.angle = math.radians(0)
                        # If the selected track is top-left.
                        elif train.selected_track.track_type == TrackType.TOP_LEFT:
                            if train.direction == Direction.RIGHT:
                                train.angle += State.angular_vel
                                if train.angle >= math.radians(90) - 0.5 * State.angular_vel:
                                    train.direction = Direction.UP
                                    train.angle = math.radians(90)
                            elif train.direction == Direction.DOWN:
                                train.angle -= State.angular_vel
                                if train.angle <= math.radians(180) + 0.5 * State.angular_vel:
                                    train.direction = Direction.LEFT
                                    train.angle = math.radians(180)
                        # If the selected track is bottom-left.
                        elif train.selected_track.track_type == TrackType.BOTTOM_LEFT:
                            if train.direction == Direction.RIGHT:
                                train.angle -= State.angular_vel
                                if train.angle <= math.radians(-90) + 0.5 * State.angular_vel:
                                    train.direction = Direction.DOWN
                                    train.angle = math.radians(270)
                            elif train.direction == Direction.UP:
                                train.angle += State.angular_vel
                                if train.angle >= math.radians(180) - 0.5 * State.angular_vel:
                                    train.direction = Direction.LEFT
                                    train.angle = math.radians(180)
                        # If the selected track is bottom-right.
                        elif train.selected_track.track_type == TrackType.BOTTOM_RIGHT:
                            if train.direction == Direction.LEFT:
                                train.angle += State.angular_vel
                                if train.angle >= math.radians(270) - 0.5 * State.angular_vel:
                                    train.direction = Direction.DOWN
                                    train.angle = math.radians(270)
                            elif train.direction == Direction.UP:
                                train.angle -= State.angular_vel
                                if train.angle <= math.radians(0) + 0.5 * State.angular_vel:
                                    train.direction = Direction.RIGHT
                                    train.angle = math.radians(0)

        # Update the cell according to mouse position.
        cell.check_mouse_collision()
        # If mouse is on the cell, the mouse is pressed, and the delete mode is on.
        if cell.mouse_on and State.mouse_pressed[0] and State.delete_mode:
            cell.tracks.clear()

    # Update trains.
    for train in State.trains:
        train.update(State.train_go)

    # Draw the train sprites.
    State.train_sprites.draw(State.screen_surface)

    # Draw the station sprites.
    State.station_sprites.draw(State.screen_surface)

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

    # Go back to main menu if requested by the user.
    if State.pressed_keys[UserControl.MAIN_MENU]:
        State.train_go = False
        for train in State.trains:
            train.reset()
        State.game_phase = Phase.MAIN_MENU
        logger.info(f"Moving to state {State.game_phase}")


# Exit phase.
def exit_phase():
    logger.info("Exiting game...")
    pg.quit()
    sys.exit()


# Check basic events, like quit.
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

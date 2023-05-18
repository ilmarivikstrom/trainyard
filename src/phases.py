import math
import sys

import pygame as pg
from pygame.locals import QUIT

from src.color_constants import DELETE_MODE_BG_COLOR, NORMAL_MODE_BG_COLOR, GRAY10, WHITESMOKE
from src.config import Config
from src.controls import UserControl
from src.field import Field, TrackType
from src.game_state import State, Direction, Phase
from src.resources import Resources
from src.sound import Sound
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


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
    if State.trains_released:
        State.screen_surface.fill(DELETE_MODE_BG_COLOR)
    else:
        State.screen_surface.fill(NORMAL_MODE_BG_COLOR)

    # Blit the color gradient on top of the base layer.
    State.gradient_dest = (-640 + 640 * math.sin(State.current_tick * 0.005), -360 + 360 * math.cos(State.current_tick * 0.005))
    State.screen_surface.blit(Resources.img_surfaces["gradient"], dest=State.gradient_dest)

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
        if State.trains_released:
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
                            train.crash()
                            State.trains_crashed += 1
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
                                logger.debug(f"Selected track: {train.selected_track.directions}")
                            else:
                                # If there are no possible tracks available. Should 'crash'.
                                train.crash()
                                logger.debug("No track to be selected. Train is not on track.")


                    # If the train has selected a track.
                    if train.selected_track is not None:
                        train.on_track = True
                        # If the selected track is vertical.
                        if train.selected_track.track_type == TrackType.VERT:
                            if train.direction == Direction.UP:
                                train.angle = math.radians(90)
                                train.pos = round(train.pos)
                            elif train.direction == Direction.DOWN:
                                train.angle = math.radians(270)
                                train.pos = round(train.pos)
                        # If the selected track is horizontal.
                        elif train.selected_track.track_type == TrackType.HORI:
                            if train.direction == Direction.RIGHT:
                                train.angle = math.radians(0)
                                train.pos = round(train.pos)
                            elif train.direction == Direction.LEFT:
                                train.angle = math.radians(180)
                                train.pos = round(train.pos)
                        # If the selected track is top-right.
                        elif train.selected_track.track_type == TrackType.TOP_RIGHT:
                            if train.direction == Direction.LEFT:
                                train.angle -= State.angular_vel
                                if train.angle <= math.radians(90) + 0.5 * State.angular_vel:
                                    train.direction = Direction.UP
                                    train.angle = math.radians(90)
                                    train.rect.center = pg.Vector2(cell.rect.midtop)
                                    train.pos = pg.Vector2(train.rect.topleft)
                            elif train.direction == Direction.DOWN:
                                train.angle += State.angular_vel
                                if train.angle >= math.radians(360) - 0.5 * State.angular_vel:
                                    train.direction = Direction.RIGHT
                                    train.angle = math.radians(0)
                                    train.rect.center = pg.Vector2(cell.rect.midright)
                                    train.pos = pg.Vector2(train.rect.topleft)
                        # If the selected track is top-left.
                        elif train.selected_track.track_type == TrackType.TOP_LEFT:
                            if train.direction == Direction.RIGHT:
                                train.angle += State.angular_vel
                                if train.angle >= math.radians(90) - 0.5 * State.angular_vel:
                                    train.direction = Direction.UP
                                    train.angle = math.radians(90)
                                    train.rect.center = pg.Vector2(cell.rect.midtop)
                                    train.pos = pg.Vector2(train.rect.topleft)
                            elif train.direction == Direction.DOWN:
                                train.angle -= State.angular_vel
                                if train.angle <= math.radians(180) + 0.5 * State.angular_vel:
                                    train.direction = Direction.LEFT
                                    train.angle = math.radians(180)
                                    train.rect.center = pg.Vector2(cell.rect.midleft)
                                    train.pos = pg.Vector2(train.rect.topleft)
                        # If the selected track is bottom-left.
                        elif train.selected_track.track_type == TrackType.BOTTOM_LEFT:
                            if train.direction == Direction.RIGHT:
                                train.angle -= State.angular_vel
                                if train.angle <= math.radians(-90) + 0.5 * State.angular_vel:
                                    train.direction = Direction.DOWN
                                    train.angle = math.radians(270)
                                    train.rect.center = pg.Vector2(cell.rect.midbottom)
                                    train.pos = pg.Vector2(train.rect.topleft)
                            elif train.direction == Direction.UP:
                                train.angle += State.angular_vel
                                if train.angle >= math.radians(180) - 0.5 * State.angular_vel:
                                    train.direction = Direction.LEFT
                                    train.angle = math.radians(180)
                                    train.rect.center = pg.Vector2(cell.rect.midleft)
                                    train.pos = pg.Vector2(train.rect.topleft)
                        # If the selected track is bottom-right.
                        elif train.selected_track.track_type == TrackType.BOTTOM_RIGHT:
                            if train.direction == Direction.LEFT:
                                train.angle += State.angular_vel
                                if train.angle >= math.radians(270) - 0.5 * State.angular_vel:
                                    train.direction = Direction.DOWN
                                    train.angle = math.radians(270)
                                    train.rect.center = pg.Vector2(cell.rect.midbottom)
                                    train.pos = pg.Vector2(train.rect.topleft)
                            elif train.direction == Direction.UP:
                                train.angle -= State.angular_vel
                                if train.angle <= math.radians(0) + 0.5 * State.angular_vel:
                                    train.direction = Direction.RIGHT
                                    train.angle = math.radians(0)
                                    train.rect.center = pg.Vector2(cell.rect.midright)
                                    train.pos = pg.Vector2(train.rect.topleft)

                    # If the cell wholly contains the train, and the last flipped cell was some other cell.
                    if cell.rect.contains(train.rect) and train.last_flipped_cell != cell:
                        # If there are 2 tracks, flip them now. TOOD: Should only flip if they intersect.
                        if len(cell.tracks) == 2:
                            cell.flip_tracks()
                            train.last_flipped_cell = cell

        # Update the cell according to mouse position.
        cell.check_mouse_collision()
        # If mouse is on the cell, the mouse is pressed, and the delete mode is on.
        if cell.mouse_on and State.mouse_pressed[0] and State.delete_mode and not State.trains_released:
            cell.tracks.clear()

    # Delete trains if 'crashed'.
    for train in State.trains:
        if train.crashed:
            State.train_sprites.remove(train)
            State.trains.remove(train)

    # TODO: Check the colors of the trains on merge.
    for train_1 in State.trains:
        other_trains = State.trains.copy()
        other_trains.remove(train_1)
        other_trains_pos = [x.pos for x in other_trains]
        other_trains_pos_dict = dict(zip(other_trains, other_trains_pos))
        if train_1.pos in other_trains_pos_dict.values():
            train_2 = [key for key, val in other_trains_pos_dict.items() if val == train_1.pos][0]
            if train_1.direction == train_2.direction:
                State.merge_trains(train_1, train_2)

    # Update trains.
    for train in State.trains:
        train.update(State.trains_released)


    # Check if collided with arrival station.
    for train in State.trains:
        if train.rect.colliderect(State.arrival_station):
            State.arrival_station.handle_train_arrival(train)
            print(f"Arrival station saveable attributes: {State.arrival_station.saveable_attributes.serialize()}")


    # Draw the train sprites.
    State.train_sprites.draw(State.screen_surface)

    # Draw the station sprites.
    State.departure_station_sprites.draw(State.screen_surface)
    State.arrival_station_sprites.draw(State.screen_surface)

    # Draw the blob sprites.
    for departure_station in State.departure_stations:
        departure_station.departure_sprites.draw(State.screen_surface)
    State.arrival_station.arrival_sprites.draw(State.screen_surface)

    # Place track on the cell based on the mouse movements.
    if State.mouse_pressed[0] and not State.delete_mode and State.prev_cell_needs_checking and not State.trains_released:
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

    if not State.level_passed:
        if State.arrival_station.number_of_trains == 0 and State.trains_crashed == 0 and len(State.trains) == 0:
            Sound.success.play()
            State.level_passed = True

    # Go back to main menu if requested by the user.
    if State.pressed_keys[UserControl.MAIN_MENU]:
        State.trains_released = False
        for train in State.trains:
            train.reset()
        State.game_phase = Phase.MAIN_MENU
        logger.info(f"Moving to state {State.game_phase}")

    pg.draw.line(State.screen_surface, WHITESMOKE, (State.screen_surface.get_width() / 2, 64), (State.screen_surface.get_width() / 2, 64 + 8 * 64))

    # Update the departure station.
    for departure_station in State.departure_stations:
        departure_station.update()


# Exit phase.
def exit_phase():
    logger.info("Exiting...")
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

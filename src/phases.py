import math
import sys
from typing import List

import pygame as pg
import pygame.gfxdraw
from pygame.locals import QUIT

from src.color_constants import (DELETE_MODE_BG_COLOR, GRAY10,
                                 NORMAL_MODE_BG_COLOR, WHITESMOKE)
from src.color_constants import GRAY, RED1, WHITE
from src.config import Config
from src.controls import UserControl
from src.direction import Direction
from src.field import Field, TrackType
from src.game_state import Phase, State
from src.resources import Resources
from src.sound import Sound
from src.station import ArrivalStation, DepartureStation
from src.track import Track
from src.train import Train
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


def update_gameplay_state(field: Field) -> None:
    UserControl.update_user_controls()

    if UserControl.pressed_keys[pg.K_SPACE] and not UserControl.wait_for_space_up:
        State.trains_released = not State.trains_released
        UserControl.wait_for_space_up = True
        logger.debug("Space down.")
    if UserControl.wait_for_space_up:
        if not UserControl.pressed_keys[pg.K_SPACE]:
            UserControl.wait_for_space_up = False
            logger.debug("Space released.")
    # TODO: Reset only once.
    if not State.trains_released:
        for station in field.stations:
            station.reset()
        State.trains.clear()
        State.train_sprites.empty()
        State.trains_crashed = 0
        State.trains_released = False
        State.level_passed = False


def main_menu_phase(field: Field) -> None:
    State.screen_surface.fill(GRAY10)
    check_events(field)
    pressed_keys = pg.key.get_pressed()
    if pressed_keys[UserControl.GAMEPLAY]:
        State.game_phase = Phase.GAMEPLAY
        logger.info(f"Moving to state {State.game_phase}")
    elif pressed_keys[UserControl.EXIT]:
        State.game_phase = Phase.GAME_END
        logger.info(f"Moving to state {State.game_phase}")


def gameplay_phase(field: Field) -> None:
    check_events(field)
    update_gameplay_state(field)

    # Check if delete mode, change background color accordingly.
    if State.trains_released:
        State.screen_surface.fill(DELETE_MODE_BG_COLOR)
    else:
        State.screen_surface.fill(NORMAL_MODE_BG_COLOR)

    # Blit the color gradient on top of the base layer.
    State.day_cycle_dest = (-State.current_tick * 0.1, 0)
    State.screen_surface.blit(Resources.img_surfaces["day_cycle"], dest=State.day_cycle_dest)

    # 1. Draw cell sprites.
    field.empties_sprites.draw(State.screen_surface)

    for train in State.trains:
        train.on_track = False
        train.at_endpoint = False

    # Iterate over all the cells on the map.
    for (_, empty_cell) in enumerate(field.empties):

        # 2. Draw track sprites on top of the cells.
        for (_, track) in enumerate(empty_cell.tracks):
            for endpoint in track.endpoints:
                for train in State.trains:
                    if pg.Vector2(train.rect.center) == endpoint:
                        train.at_endpoint = True
            if track.bright == True:
                color = WHITE
            else:
                color = GRAY
            if track.image:
                State.screen_surface.blit(track.image, dest=track.cell_rect)
            if Config.draw_arcs:
                if track.track_type == TrackType.VERT:
                    pg.draw.line(State.screen_surface, color, track.cell_rect.midtop, track.cell_rect.midbottom)
                elif track.track_type == TrackType.HORI:
                    pg.draw.line(State.screen_surface, color, track.cell_rect.midleft, track.cell_rect.midright)
                elif track.track_type == TrackType.TOP_RIGHT:
                    pygame.gfxdraw.arc(State.screen_surface, track.cell_rect.right, track.cell_rect.top, int(Config.cell_size / 2), 90, 180, color)
                elif track.track_type == TrackType.TOP_LEFT:
                    pygame.gfxdraw.arc(State.screen_surface, track.cell_rect.left, track.cell_rect.top, int(Config.cell_size / 2), 0, 90, color)
                elif track.track_type == TrackType.BOTTOM_LEFT:
                    pygame.gfxdraw.arc(State.screen_surface, track.cell_rect.left, track.cell_rect.bottom, int(Config.cell_size / 2), 270, 360, color)
                elif track.track_type == TrackType.BOTTOM_RIGHT:
                    pygame.gfxdraw.arc(State.screen_surface, track.cell_rect.right, track.cell_rect.bottom, int(Config.cell_size / 2), 180, 270, color)

                for endpoint in track.endpoints:
                    pygame.gfxdraw.pixel(State.screen_surface, int(endpoint.x), int(endpoint.y), RED1)


        # If train 'release' command has been given.
        if State.trains_released:
            for train in State.trains:
                # If the cell in question intersects with the center of the train.
                if empty_cell.rect.colliderect(pg.Rect(train.rect.centerx - 1, train.rect.centery - 1, 1, 1)):
                    # If this is a new cell OR there is no info about the selected track.
                    if empty_cell not in train.last_collided_cells or train.selected_track is None:
                        # Add the cell to the last collided cells.
                        train.last_collided_cells.append(empty_cell)
                        train.last_collided_cells = train.last_collided_cells[-2:]
                        # Reset the last flipped cell.
                        train.last_flipped_cell = None
                        # If there are no tracks in this cell.
                        if len(empty_cell.tracks) == 0:
                            # Stop the train. Should mean 'crash'.
                            train.crash()
                            State.trains_crashed += 1
                        else:
                            # If there are some tracks in this cell.
                            train.tracks_ahead = empty_cell.tracks
                            possible_tracks: List[Track] = []
                            # If the state has just been reset, select the only available track.
                            if train.is_reset:
                                possible_tracks.append(empty_cell.tracks[0])
                            else:
                                # Let's find all tracks in this cell that have an endpoint where the train is.
                                for track_ahead in empty_cell.tracks:
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
                                if train.selected_track:
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
                                train.pos = pg.Vector2(round(train.pos.x), round(train.pos.y))
                            elif train.direction == Direction.DOWN:
                                train.angle = math.radians(270)
                                train.pos = pg.Vector2(round(train.pos.x), round(train.pos.y))
                        # If the selected track is horizontal.
                        elif train.selected_track.track_type == TrackType.HORI:
                            if train.direction == Direction.RIGHT:
                                train.angle = math.radians(0)
                                train.pos = pg.Vector2(round(train.pos.x), round(train.pos.y))
                            elif train.direction == Direction.LEFT:
                                train.angle = math.radians(180)
                                train.pos = pg.Vector2(round(train.pos.x), round(train.pos.y))
                        # If the selected track is top-right.
                        elif train.selected_track.track_type == TrackType.TOP_RIGHT:
                            if train.direction == Direction.LEFT:
                                train.angle -= Config.angular_vel
                                if train.angle <= math.radians(90) + 0.5 * Config.angular_vel:
                                    train.direction = Direction.UP
                                    train.angle = math.radians(90)
                                    train.rect.center = pg.Vector2(empty_cell.rect.midtop)
                                    train.pos = pg.Vector2(train.rect.topleft)
                            elif train.direction == Direction.DOWN:
                                train.angle += Config.angular_vel
                                if train.angle >= math.radians(360) - 0.5 * Config.angular_vel:
                                    train.direction = Direction.RIGHT
                                    train.angle = math.radians(0)
                                    train.rect.center = pg.Vector2(empty_cell.rect.midright)
                                    train.pos = pg.Vector2(train.rect.topleft)
                        # If the selected track is top-left.
                        elif train.selected_track.track_type == TrackType.TOP_LEFT:
                            if train.direction == Direction.RIGHT:
                                train.angle += Config.angular_vel
                                if train.angle >= math.radians(90) - 0.5 * Config.angular_vel:
                                    train.direction = Direction.UP
                                    train.angle = math.radians(90)
                                    train.rect.center = pg.Vector2(empty_cell.rect.midtop)
                                    train.pos = pg.Vector2(train.rect.topleft)
                            elif train.direction == Direction.DOWN:
                                train.angle -= Config.angular_vel
                                if train.angle <= math.radians(180) + 0.5 * Config.angular_vel:
                                    train.direction = Direction.LEFT
                                    train.angle = math.radians(180)
                                    train.rect.center = pg.Vector2(empty_cell.rect.midleft)
                                    train.pos = pg.Vector2(train.rect.topleft)
                        # If the selected track is bottom-left.
                        elif train.selected_track.track_type == TrackType.BOTTOM_LEFT:
                            if train.direction == Direction.RIGHT:
                                train.angle -= Config.angular_vel
                                if train.angle <= math.radians(-90) + 0.5 * Config.angular_vel:
                                    train.direction = Direction.DOWN
                                    train.angle = math.radians(270)
                                    train.rect.center = pg.Vector2(empty_cell.rect.midbottom)
                                    train.pos = pg.Vector2(train.rect.topleft)
                            elif train.direction == Direction.UP:
                                train.angle += Config.angular_vel
                                if train.angle >= math.radians(180) - 0.5 * Config.angular_vel:
                                    train.direction = Direction.LEFT
                                    train.angle = math.radians(180)
                                    train.rect.center = pg.Vector2(empty_cell.rect.midleft)
                                    train.pos = pg.Vector2(train.rect.topleft)
                        # If the selected track is bottom-right.
                        elif train.selected_track.track_type == TrackType.BOTTOM_RIGHT:
                            if train.direction == Direction.LEFT:
                                train.angle += Config.angular_vel
                                if train.angle >= math.radians(270) - 0.5 * Config.angular_vel:
                                    train.direction = Direction.DOWN
                                    train.angle = math.radians(270)
                                    train.rect.center = pg.Vector2(empty_cell.rect.midbottom)
                                    train.pos = pg.Vector2(train.rect.topleft)
                            elif train.direction == Direction.UP:
                                train.angle -= Config.angular_vel
                                if train.angle <= math.radians(0) + 0.5 * Config.angular_vel:
                                    train.direction = Direction.RIGHT
                                    train.angle = math.radians(0)
                                    train.rect.center = pg.Vector2(empty_cell.rect.midright)
                                    train.pos = pg.Vector2(train.rect.topleft)

                    # If the cell wholly contains the train, and the last flipped cell was some other cell.
                    if empty_cell.rect and empty_cell.rect.contains(train.rect) and train.last_flipped_cell != empty_cell:
                        # If there are 2 tracks, flip them now. TOOD: Should only flip if they intersect.
                        if len(empty_cell.tracks) == 2:
                            empty_cell.flip_tracks()
                            train.last_flipped_cell = empty_cell

        # Update the cell according to mouse position.
        if empty_cell.check_mouse_collision():
            State.prev_cell_needs_checking = True
        # If mouse is on the cell, the mouse is pressed, and the delete mode is on.
        if empty_cell.mouse_on and UserControl.mouse_pressed[0] and UserControl.delete_mode and not State.trains_released:
            empty_cell.tracks.clear()


    # Check if trains should merge, or if they have crashed.
    for train_1 in State.trains:
        other_trains = State.trains.copy()
        other_trains.remove(train_1)
        other_trains_pos = [x.pos for x in other_trains]
        other_trains_pos_dict = dict(zip(other_trains, other_trains_pos))
        if train_1.pos in other_trains_pos_dict.values():
            train_2 = [key for key, val in other_trains_pos_dict.items() if val == train_1.pos][0]
            if train_1.direction == train_2.direction:
                State.merge_trains(train_1, train_2)


    # Delete trains if 'crashed'.
    for train in State.trains:
        if train.crashed:
            State.train_sprites.remove(train)
            State.trains.remove(train)
            logger.info(f"Train crashed. Trains left: {len(State.trains)}")


    # Update trains.
    for train in State.trains:
        train.tick(State.trains_released)


    # Check if collided with arrival station.
    for train in State.trains:
        for station in field.stations:
            if isinstance(station, ArrivalStation):
                if train.rect.colliderect(station):
                    if train.color == station.train_color and station.goals and station.number_of_trains_left > 0:
                        station.is_reset = False
                        station.number_of_trains_left -= 1
                        station.goals.pop().kill()
                        logger.debug(f"Caught a train! Number of trains still expecting: {station.number_of_trains_left}")
                        Sound.play_sound_on_channel(Sound.pop, 1)
                    else:
                        logger.debug("CRASH! Wrong color train or not expecting further arrivals.")
                        train.crash()
                        State.trains_crashed += 1
                    train.kill()
                    State.trains.remove(train)
                    logger.info(f"Arrival station saveable attributes: {station.saveable_attributes.serialize()}")


    # Draw the train sprites.
    State.train_sprites.draw(State.screen_surface)

    # Draw the station sprites.
    field.stations_sprites.draw(State.screen_surface)

    # Draw the blob sprites.
    for station in field.stations:
        station.goal_sprites.draw(State.screen_surface)

    # Place track on the cell based on the mouse movements.
    if UserControl.mouse_pressed[0] and not UserControl.delete_mode and State.prev_cell_needs_checking and not State.trains_released:
        if UserControl.prev_cell and UserControl.curr_cell:
            if (UserControl.prev_movement == Direction.UP and UserControl.curr_movement == Direction.UP) or (UserControl.prev_movement == Direction.DOWN and UserControl.curr_movement == Direction.DOWN):
                field.place_track_item(TrackType.VERT, UserControl.prev_cell)
            elif (UserControl.prev_movement == Direction.RIGHT and UserControl.curr_movement == Direction.RIGHT) or (UserControl.prev_movement == Direction.LEFT and UserControl.curr_movement == Direction.LEFT):
                field.place_track_item(TrackType.HORI, UserControl.prev_cell)
            elif (UserControl.prev_movement == Direction.UP and UserControl.curr_movement == Direction.LEFT) or (UserControl.prev_movement == Direction.RIGHT and UserControl.curr_movement == Direction.DOWN):
                field.place_track_item(TrackType.BOTTOM_LEFT, UserControl.prev_cell)
            elif (UserControl.prev_movement == Direction.UP and UserControl.curr_movement == Direction.RIGHT) or (UserControl.prev_movement == Direction.LEFT and UserControl.curr_movement == Direction.DOWN):
                field.place_track_item(TrackType.BOTTOM_RIGHT, UserControl.prev_cell)
            elif (UserControl.prev_movement == Direction.DOWN and UserControl.curr_movement == Direction.RIGHT) or (UserControl.prev_movement == Direction.LEFT and UserControl.curr_movement == Direction.UP):
                field.place_track_item(TrackType.TOP_RIGHT, UserControl.prev_cell)
            elif (UserControl.prev_movement == Direction.DOWN and UserControl.curr_movement == Direction.LEFT) or (UserControl.prev_movement == Direction.RIGHT and UserControl.curr_movement == Direction.UP):
                field.place_track_item(TrackType.TOP_LEFT, UserControl.prev_cell)

    if not State.level_passed:
        arrival_stations_pending = False
        for station in field.stations:
            if isinstance(station, ArrivalStation):
                if station.number_of_trains_left > 0:
                    arrival_stations_pending = True
        if not arrival_stations_pending and State.trains_crashed == 0 and len(State.trains) == 0:
            Sound.success.play()
            State.level_passed = True

    # Go back to main menu if requested by the user.
    if UserControl.pressed_keys[UserControl.MAIN_MENU]:
        State.trains_released = False
        for train in State.trains:
            train.reset()
        State.game_phase = Phase.MAIN_MENU
        logger.info(f"Moving to state {State.game_phase}")

    pg.draw.line(State.screen_surface, WHITESMOKE, (State.screen_surface.get_width() / 2, 64), (State.screen_surface.get_width() / 2, 64 + 8 * 64))

    # Update the departure station.
    for station in field.stations:
        if isinstance(station, DepartureStation):
            if State.trains_released and station.number_of_trains_left > 0:
                station.is_reset = False
                if not station.last_release_tick or State.current_tick - station.last_release_tick == 32:
                    train_to_release = Train(station.i, station.j, station.train_color, Direction(station.angle))
                    State.trains.append(train_to_release)
                    State.train_sprites.add(train_to_release)
                    station.number_of_trains_left -= 1
                    station.goals.pop().kill()
                    logger.debug("Train released.")
                    station.last_release_tick = State.current_tick
                    Sound.play_sound_on_channel(Sound.pop, 1)
                    logger.info(f"Departure station saveable attributes: {station.saveable_attributes.serialize()}")


# Exit phase.
def exit_phase():
    logger.info("Exiting...")
    pg.quit()
    sys.exit()


# Check basic events, like quit.
def check_events(field: Field) -> None:
    for event in pg.event.get():
        if event.type == QUIT:
            State.game_phase = Phase.GAME_END
            logger.info(f"Moving to state {State.game_phase}")
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                for cell in field.empties:
                    if cell.mouse_on:
                        cell.flip_tracks()

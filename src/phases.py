import math
import sys
from typing import List

import pygame as pg
import pygame.gfxdraw
from pygame.locals import QUIT, MOUSEBUTTONDOWN

from src.cell import EmptyCell
from src.color_constants import (DELETE_MODE_BG_COLOR, GRAY10,
                                 NORMAL_MODE_BG_COLOR, WHITESMOKE)
from src.color_constants import GRAY, RED1, WHITE
from src.config import Config
from src.controls import UserControl
from src.direction import Direction
from src.field import Field, TrackType
from src.game_state import Phase, State
from src.resources import Graphics
from src.sound import Sound
from src.station import ArrivalStation, DepartureStation, CheckmarkSprite
from src.track import Track
from src.train import Train
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


def update_gameplay_state(field: Field) -> None:
    UserControl.update_user_control_state()
    check_delete_mode()

    if UserControl.check_space_down_event():
        State.trains_released = not State.trains_released
    _ = UserControl.check_space_released_event()

    if not State.trains_released and not State.trains:
        for station in field.stations:
            station.reset()
        State.trains.clear()
        State.train_sprites.empty() #type: ignore
        State.trains_crashed = 0
        State.trains_released = False
        State.level_passed = False


def check_delete_mode() -> None:
    if UserControl.pressed_keys[UserControl.DELETE_MODE]:
        State.in_delete_mode = True
    else:
        State.in_delete_mode = False


def check_for_gameplay_command() -> None:
    if UserControl.pressed_keys[UserControl.GAMEPLAY]:
        State.game_phase = Phase.GAMEPLAY
        logger.info(f"Moving to state {State.game_phase}")


def check_for_exit_command() -> None:
    if UserControl.pressed_keys[UserControl.EXIT]:
        State.game_phase = Phase.GAME_END
        logger.info(f"Moving to state {State.game_phase}")


def main_menu_phase(field: Field) -> None:
    UserControl.update_user_control_state()
    State.screen_surface.fill(GRAY10)
    check_events(field)
    check_for_gameplay_command()
    check_for_exit_command()


def draw_arcs_and_endpoints(track: Track):
    if track.bright:
        color = WHITE
    else:
        color = GRAY
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


def draw_background_basecolor() -> None:
    if State.trains_released:
        State.screen_surface.fill(DELETE_MODE_BG_COLOR)
    else:
        State.screen_surface.fill(NORMAL_MODE_BG_COLOR)


def draw_background_day_cycle() -> None:
    State.day_cycle_dest = (-State.current_tick * 0.1, 0)
    State.screen_surface.blit(Graphics.img_surfaces["day_cycle"], dest=State.day_cycle_dest)


def draw_empty_cell_tracks(empty_cell: EmptyCell) -> None:
    for track in empty_cell.tracks:
        if track.image:
            State.screen_surface.blit(track.image, dest=track.cell_rect)
        if Config.draw_arcs:
            draw_arcs_and_endpoints(track)


def delete_crashed_trains() -> None:
    for train in State.trains:
        if train.crashed:
            State.train_sprites.remove(train) # type: ignore
            State.trains.remove(train)
            logger.info(f"Train crashed. Trains left: {len(State.trains)}")


def tick_trains() -> None:
    for train in State.trains:
        train.tick(State.trains_released)


def check_train_arrivals(field: Field) -> None:
    for train in State.trains:
        for station in field.stations:
            if station.rect is None:
                raise ValueError(f"The rect of {station} is None.")
            if isinstance(station, ArrivalStation) and train.rect.colliderect(station.rect):
                if train.color == station.train_color and station.goals and station.number_of_trains_left > 0:
                    State.trains.remove(train)
                    State.train_sprites.remove(train) # type: ignore
                    station.is_reset = False
                    station.number_of_trains_left -= 1
                    station.goals.pop().kill()
                    logger.debug(f"Caught a train! Number of trains still expecting: {station.number_of_trains_left}")
                    Sound.play_sound_on_channel(Sound.pop, 1)
                else:
                    logger.debug("CRASH! Wrong color train or not expecting further arrivals.")
                    train.crash()
                    State.trains_crashed += 1
                logger.info(f"Arrival station saveable attributes: {station.saveable_attributes.serialize()}")


def determine_arrival_station_checkmarks(field: Field) -> None:
    for station in field.stations:
        if isinstance(station, ArrivalStation) and station.number_of_trains_left == 0 and station.rect is not None:
            station.checkmark = CheckmarkSprite(station.rect)
        else:
            station.checkmark = None



def draw_station_goals(field: Field) -> None:
    for station in field.stations:
        station.goal_sprites.draw(State.screen_surface) # type: ignore


def draw_separator_line() -> None:
    pg.draw.line(State.screen_surface, WHITESMOKE, (State.screen_surface.get_width() / 2, 64), (State.screen_surface.get_width() / 2, 64 + 8 * 64))


def add_new_train(train: Train) -> None:
    State.trains.append(train)
    State.train_sprites.add(train) # type: ignore


def tick_departures(field: Field) -> None:
    if not State.trains_released:
        return
    for station in field.stations:
        if isinstance(station, DepartureStation):
            res = station.tick(State.current_tick)
            if isinstance(res, Train):
                add_new_train(res)


def check_for_main_menu_command() -> None:
    if UserControl.pressed_keys[UserControl.MAIN_MENU]:
        State.trains_released = False
        for train in State.trains:
            train.reset()
        State.game_phase = Phase.MAIN_MENU
        logger.info(f"Moving to state {State.game_phase}")


def arrivals_pending(field: Field) -> bool:
    for station in field.stations:
        if isinstance(station, ArrivalStation) and station.number_of_trains_left > 0:
            return True
    return False


def check_for_level_completion(field: Field) -> None:
    if not State.level_passed and not arrivals_pending(field) and State.trains_crashed == 0 and len(State.trains) == 0:
        Sound.success.play()
        State.level_passed = True


def reset_train_statuses() -> None:
    for train in State.trains:
        train.on_track = False


def check_track_delete(empty_cell: EmptyCell) -> None:
    mouse_pressed_cell_while_in_delete_mode = (empty_cell.mouse_on and UserControl.mouse_pressed[0] and State.in_delete_mode and not State.trains_released)
    if mouse_pressed_cell_while_in_delete_mode:
        empty_cell.tracks.clear()


def move_train_along_selected_track(train: Train, empty_cell: EmptyCell) -> None:
    # If the train has selected a track.
    if train.selected_track is not None and empty_cell.rect is not None:
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
                    train.rect.center = empty_cell.rect.midtop
                    train.pos = pg.Vector2(train.rect.topleft)
            elif train.direction == Direction.DOWN:
                train.angle += Config.angular_vel
                if train.angle >= math.radians(360) - 0.5 * Config.angular_vel:
                    train.direction = Direction.RIGHT
                    train.angle = math.radians(0)
                    train.rect.center = empty_cell.rect.midright
                    train.pos = pg.Vector2(train.rect.topleft)
        # If the selected track is top-left.
        elif train.selected_track.track_type == TrackType.TOP_LEFT:
            if train.direction == Direction.RIGHT:
                train.angle += Config.angular_vel
                if train.angle >= math.radians(90) - 0.5 * Config.angular_vel:
                    train.direction = Direction.UP
                    train.angle = math.radians(90)
                    train.rect.center = empty_cell.rect.midtop
                    train.pos = pg.Vector2(train.rect.topleft)
            elif train.direction == Direction.DOWN:
                train.angle -= Config.angular_vel
                if train.angle <= math.radians(180) + 0.5 * Config.angular_vel:
                    train.direction = Direction.LEFT
                    train.angle = math.radians(180)
                    train.rect.center = empty_cell.rect.midleft
                    train.pos = pg.Vector2(train.rect.topleft)
        # If the selected track is bottom-left.
        elif train.selected_track.track_type == TrackType.BOTTOM_LEFT:
            if train.direction == Direction.RIGHT:
                train.angle -= Config.angular_vel
                if train.angle <= math.radians(-90) + 0.5 * Config.angular_vel:
                    train.direction = Direction.DOWN
                    train.angle = math.radians(270)
                    train.rect.center = empty_cell.rect.midbottom
                    train.pos = pg.Vector2(train.rect.topleft)
            elif train.direction == Direction.UP:
                train.angle += Config.angular_vel
                if train.angle >= math.radians(180) - 0.5 * Config.angular_vel:
                    train.direction = Direction.LEFT
                    train.angle = math.radians(180)
                    train.rect.center = empty_cell.rect.midleft
                    train.pos = pg.Vector2(train.rect.topleft)
        # If the selected track is bottom-right.
        elif train.selected_track.track_type == TrackType.BOTTOM_RIGHT:
            if train.direction == Direction.LEFT:
                train.angle += Config.angular_vel
                if train.angle >= math.radians(270) - 0.5 * Config.angular_vel:
                    train.direction = Direction.DOWN
                    train.angle = math.radians(270)
                    train.rect.center = empty_cell.rect.midbottom
                    train.pos = pg.Vector2(train.rect.topleft)
            elif train.direction == Direction.UP:
                train.angle -= Config.angular_vel
                if train.angle <= math.radians(0) + 0.5 * Config.angular_vel:
                    train.direction = Direction.RIGHT
                    train.angle = math.radians(0)
                    train.rect.center = empty_cell.rect.midright
                    train.pos = pg.Vector2(train.rect.topleft)


def flip_tracks_if_needed(train: Train, empty_cell: EmptyCell) -> None:
    empty_cell_contains_train_and_has_multiple_tracks = (empty_cell.rect and empty_cell.rect.contains(train.rect) and train.last_flipped_cell != empty_cell and len(empty_cell.tracks) == 2)
    if empty_cell_contains_train_and_has_multiple_tracks:
        empty_cell.flip_tracks()
        train.last_flipped_cell = empty_cell


def check_train_merges() -> None:
    for train_1 in State.trains:
        other_trains = State.trains.copy()
        other_trains.remove(train_1)
        other_trains_pos = [x.pos for x in other_trains]
        other_trains_pos_dict = dict(zip(other_trains, other_trains_pos))
        if train_1.pos not in other_trains_pos_dict.values():
            continue
        train_2 = [key for key, val in other_trains_pos_dict.items() if val == train_1.pos][0]
        if train_1.direction == train_2.direction:
            State.merge_trains(train_1, train_2)


def check_for_new_track_placement(field: Field) -> None:
    left_mouse_down_in_draw_mode = (UserControl.mouse_pressed[0] and not State.in_delete_mode and not State.trains_released)
    mouse_moved_over_cells = (UserControl.prev_cell and UserControl.curr_cell)

    if left_mouse_down_in_draw_mode and mouse_moved_over_cells and State.prev_cell_needs_checking:
        mouse_moved_up =        (UserControl.prev_movement == Direction.UP      and UserControl.curr_movement == Direction.UP)
        mouse_moved_down =      (UserControl.prev_movement == Direction.DOWN    and UserControl.curr_movement == Direction.DOWN)
        mouse_moved_right =     (UserControl.prev_movement == Direction.RIGHT   and UserControl.curr_movement == Direction.RIGHT)
        mouse_moved_left =      (UserControl.prev_movement == Direction.LEFT    and UserControl.curr_movement == Direction.LEFT)
        moues_moved_upleft =    (UserControl.prev_movement == Direction.UP      and UserControl.curr_movement == Direction.LEFT)
        mouse_moved_rightdown = (UserControl.prev_movement == Direction.RIGHT   and UserControl.curr_movement == Direction.DOWN)
        mouse_moved_upright =   (UserControl.prev_movement == Direction.UP      and UserControl.curr_movement == Direction.RIGHT)
        mouse_moved_leftdown =  (UserControl.prev_movement == Direction.LEFT    and UserControl.curr_movement == Direction.DOWN)
        mouse_moved_downright = (UserControl.prev_movement == Direction.DOWN    and UserControl.curr_movement == Direction.RIGHT)
        mouse_moved_leftup =    (UserControl.prev_movement == Direction.LEFT    and UserControl.curr_movement == Direction.UP)
        mouse_moved_downleft =  (UserControl.prev_movement == Direction.DOWN    and UserControl.curr_movement == Direction.LEFT)
        mouse_moved_rightup =   (UserControl.prev_movement == Direction.RIGHT   and UserControl.curr_movement == Direction.UP)
        if mouse_moved_up or mouse_moved_down:
            field.insert_track_to_position(TrackType.VERT, UserControl.prev_cell)
        elif mouse_moved_right or mouse_moved_left:
            field.insert_track_to_position(TrackType.HORI, UserControl.prev_cell)
        elif moues_moved_upleft or mouse_moved_rightdown:
            field.insert_track_to_position(TrackType.BOTTOM_LEFT, UserControl.prev_cell)
        elif mouse_moved_upright or mouse_moved_leftdown:
            field.insert_track_to_position(TrackType.BOTTOM_RIGHT, UserControl.prev_cell)
        elif mouse_moved_downright or mouse_moved_leftup:
            field.insert_track_to_position(TrackType.TOP_RIGHT, UserControl.prev_cell)
        elif mouse_moved_downleft or mouse_moved_rightup:
            field.insert_track_to_position(TrackType.TOP_LEFT, UserControl.prev_cell)
        State.prev_cell_needs_checking = False


def display_checkmarks(field: Field) -> None:
    for station in field.stations:
        if not isinstance(station, ArrivalStation) or station.checkmark is None or station.checkmark.image is None or station.rect is None:
            continue
        State.screen_surface.blit(source=station.checkmark.image, dest=station.rect.topleft)


def check_profiling_command() -> None:
    if UserControl.pressed_keys[pg.K_F1]:
        State.profiler.continue_profiling()
    else:
        State.profiler.discontinue_profiling()


def gameplay_phase(field: Field) -> None:
    check_events(field)
    check_profiling_command()
    update_gameplay_state(field)
    draw_background_basecolor()
    draw_background_day_cycle()

    field.empty_cells_sprites.draw(State.screen_surface)

    reset_train_statuses()

    for empty_cell in field.empty_cells:
        if empty_cell.rect is None:
            raise ValueError("The cell's rect is None. Exiting.")

        draw_empty_cell_tracks(empty_cell)

        # Update the cell according to mouse position.
        if empty_cell.check_mouse_collision():
            State.prev_cell_needs_checking = True
        check_track_delete(empty_cell)

        if not State.trains_released or len(State.trains) == 0:
            continue

        for train in State.trains:
            # Continue looping if the cell does not intersect with the train.
            if not empty_cell.rect.colliderect(pg.Rect(train.rect.centerx - 1, train.rect.centery - 1, 1, 1)):
                continue

            entering_new_cell_and_track_not_selected = (empty_cell not in train.last_collided_cells or train.selected_track is None)
            if entering_new_cell_and_track_not_selected:
                train.add_last_collided_cell(empty_cell)
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

            move_train_along_selected_track(train, empty_cell)
            flip_tracks_if_needed(train, empty_cell)


    check_train_merges()
    check_train_arrivals(field)
    delete_crashed_trains()
    tick_trains()
    State.train_sprites.draw(State.screen_surface) # type: ignore
    field.stations_sprites.draw(State.screen_surface) # type: ignore
    draw_station_goals(field)

    check_for_new_track_placement(field)
    check_for_level_completion(field)
    check_for_main_menu_command()
    draw_separator_line()
    tick_departures(field)

    determine_arrival_station_checkmarks(field)
    display_checkmarks(field)


def exit_phase():
    logger.info("Exiting...")
    pg.quit()
    sys.exit()


def check_events(field: Field) -> None:
    for event in pg.event.get():
        if event.type == QUIT:
            State.game_phase = Phase.GAME_END
            logger.info(f"Moving to state {State.game_phase}")
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 3:
                for cell in field.empty_cells:
                    if cell.mouse_on and not State.trains_released and len(cell.tracks) > 1:
                        cell.flip_tracks()

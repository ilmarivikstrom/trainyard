import csv
import math
import sys
from typing import List

import pygame as pg
import pygame.gfxdraw
from pygame.locals import QUIT, MOUSEBUTTONDOWN

from src.cell import Cell, EmptyCell
from src.color_constants import (DELETE_MODE_BG_COLOR, GRAY10,
                                 NORMAL_MODE_BG_COLOR, WHITESMOKE)
from src.color_constants import GRAY, RED1, WHITE
from src.config import Config
from src.controls import UserControl
from src.direction import Direction
from src.field import Field, TrackType
from src.game_state import Phase, State
from src.graphics import Graphics
from src.screen import Screen
from src.sound import Sound
from src.station import CheckmarkSprite
from src.track import Track
from src.train import Train
from src.traincolor import blend_train_colors
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


def check_for_gameplay_command(state: State) -> None:
    if UserControl.pressed_keys[UserControl.GAMEPLAY]:
        state.game_phase = Phase.GAMEPLAY
        logger.info(f"Moving to state {state.game_phase}")


def check_for_main_menu_command(state: State) -> None:
    if UserControl.pressed_keys[UserControl.MAIN_MENU]:
        state.gameplay.reset()
        state.game_phase = Phase.MAIN_MENU
        logger.info(f"Moving to state {state.game_phase}")


def check_for_exit_command(state: State) -> None:
    if UserControl.pressed_keys[UserControl.EXIT]:
        state.game_phase = Phase.GAME_END
        logger.info(f"Moving to state {state.game_phase}")


def check_and_toggle_profiling(state: State) -> None:
    if UserControl.pressed_keys[pg.K_F1]:
        state.profiler.continue_profiling()
    else:
        state.profiler.discontinue_profiling()


def determine_arrival_station_checkmarks(field: Field) -> None:
    for arrival_station in field.arrival_stations:
        if arrival_station.number_of_trains_left == 0 and arrival_station.rect is not None:
            arrival_station.checkmark = CheckmarkSprite(arrival_station.rect)


def arrivals_pending(field: Field) -> bool:
    for arrival_station in field.arrival_stations:
        if arrival_station.number_of_trains_left > 0:
            return True
    return False


def reset_train_statuses(field: Field) -> None:
    for train in field.trains:
        train.on_track = False


def check_train_merges(field: Field) -> None:
    for train_1 in field.trains:
        other_trains = field.trains.copy()
        other_trains.remove(train_1)
        other_trains_pos = [x.pos for x in other_trains]
        other_trains_pos_dict = dict(zip(other_trains, other_trains_pos))
        if train_1.pos not in other_trains_pos_dict.values():
            continue
        train_2 = [key for key, val in other_trains_pos_dict.items() if val == train_1.pos][0]
        if train_1.direction == train_2.direction:
            merge_trains(train_1, train_2, field)
        else:
            paint_trains(train_1, train_2)


def delete_crashed_trains(field: Field) -> None:
    for train in field.trains:
        if train.crashed:
            field.train_sprites.remove(train) # type: ignore
            field.trains.remove(train)
            logger.info(f"Train crashed. Trains left: {len(field.trains)}")


def check_and_save_field(field: Field, file_name: str="level_tmp.csv") -> None:
    if UserControl.pressed_keys[UserControl.SAVE_GAME]:
        file_path = f"levels/{file_name}"
        with open(file_path, newline="", mode="w", encoding="utf-8") as level_file:
            level_writer = csv.writer(level_file, delimiter="-")
            row: List[str] = []
            for i, cell in enumerate(field.full_grid):
                row.append(cell.saveable_attributes.serialize())
                if (i+1) % 8 == 0:
                    level_writer.writerow(row)
                    row.clear()
        logger.info(f"Saved game to '{file_path}'")


def update_gameplay_state(state: State, field: Field) -> None:
    UserControl.update_user_control_state()

    if UserControl.pressed_keys[UserControl.DELETE_MODE]:
        state.gameplay.delete_mode = True
    else:
        state.gameplay.delete_mode = False

    if UserControl.space_down_event():
        state.gameplay.trains_released = not state.gameplay.trains_released
    UserControl.check_space_released_event()

    if not state.gameplay.trains_released:
        reset_to_beginning(state, field)


def reset_to_beginning(state: State, field: Field) -> None:
    field.reset()
    state.gameplay.reset()


def tick_trains(state: State, field: Field) -> None:
    for train in field.trains:
        train.tick(state.gameplay.trains_released)


def check_train_arrivals(state: State, field: Field) -> None:
    for train in field.trains:
        for arrival_station in field.arrival_stations:
            if arrival_station.rect is None:
                raise ValueError(f"The rect of {arrival_station} is None.")
            if train.rect.collidepoint(arrival_station.rect.center):
                if train.color == arrival_station.train_color and arrival_station.goals and arrival_station.number_of_trains_left > 0:
                    field.trains.remove(train)
                    field.train_sprites.remove(train) # type: ignore
                    arrival_station.is_reset = False
                    arrival_station.number_of_trains_left -= 1
                    arrival_station.goals.pop().kill()
                    logger.debug(f"Caught a train! Number of trains still expecting: {arrival_station.number_of_trains_left}")
                    Sound.play_sound_on_channel(Sound.pop, 1)
                else:
                    logger.debug("CRASH! Wrong color train or not expecting further arrivals.")
                    train.crash()
                    state.gameplay.trains_crashed += 1
                    arrival_station.checkmark = None
                logger.info(f"Arrival station saveable attributes: {arrival_station.saveable_attributes.serialize()}")


def tick_departures(state: State, field: Field) -> None:
    if not state.gameplay.trains_released:
        return
    for departure_station in field.departure_stations:
        res = departure_station.tick(state.global_status.current_tick)
        if res is not None:
            add_new_train(field, res)


def check_for_level_completion(state: State, field: Field) -> None:
    if not state.gameplay.current_level_passed and not arrivals_pending(field) and state.gameplay.trains_crashed == 0 and len(field.trains) == 0:
        Sound.success.play()
        state.gameplay.current_level_passed = True


def check_for_new_track_placement(state: State, field: Field) -> None:
    left_mouse_down_in_draw_mode = (UserControl.mouse_pressed[0] and not state.gameplay.delete_mode and not state.gameplay.trains_released)
    mouse_moved_over_cells = (UserControl.prev_cell and UserControl.curr_cell)
    if left_mouse_down_in_draw_mode and mouse_moved_over_cells and state.gameplay.prev_cell_needs_checking:
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
        state.gameplay.prev_cell_needs_checking = False


def check_for_pygame_events(state: State, field: Field) -> None:
    for event in pg.event.get():
        if event.type == QUIT:
            state.game_phase = Phase.GAME_END
            logger.info(f"Moving to state {state.game_phase}")
        elif event.type == MOUSEBUTTONDOWN and event.button == 3:
            for empty_cell in field.empty_cells:
                if empty_cell.mouse_on and not state.gameplay.trains_released and len(empty_cell.tracks) > 1:
                    empty_cell.flip_tracks()


def select_tracks_and_move_trains(state: State, field: Field) -> None:
    for cell in field.full_grid:
        if cell.check_mouse_collision():
            state.gameplay.prev_cell_needs_checking = True
        for train in field.trains:
            if cell.rect is None:
                raise ValueError("Rect is None.")
            if not cell.rect.colliderect(pg.Rect(train.rect.centerx - 1, train.rect.centery - 1, 1, 1)):
                continue
            entering_new_cell_and_track_not_selected = (cell not in train.last_collided_cells or train.selected_track is None)
            if entering_new_cell_and_track_not_selected:
                train.add_last_collided_cell(cell)
                # Reset the last flipped cell.
                train.last_flipped_cell = None
                # If there are no tracks in this cell.
                if len(cell.tracks) == 0:
                    # Stop the train. Should mean 'crash'.
                    train.crash()
                    state.gameplay.trains_crashed += 1
                else:
                    # If there are some tracks in this cell.
                    train.tracks_ahead = cell.tracks
                    possible_tracks: List[Track] = []
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
                        if train.selected_track:
                            logger.debug(f"Selected track: {train.selected_track.directions}")
                    else:
                        # If there are no possible tracks available. Should 'crash'.
                        train.crash()
                        logger.debug("No track to be selected. Train is not on track.")
            move_train_along_cell(train, cell)
            check_and_flip_cell_tracks(train, cell)


def check_and_delete_field_tracks(state: State, field: Field) -> None:
    for empty_cell in field.empty_cells:
        if empty_cell.rect is None:
            raise ValueError("The cell's rect is None. Exiting.")
        check_and_delete_empty_cell_tracks(state, empty_cell)


def add_new_train(field: Field, train: Train) -> None:
    field.trains.append(train)
    field.train_sprites.add(train) # type: ignore


def check_and_delete_empty_cell_tracks(state: State, empty_cell: EmptyCell) -> None:
    mouse_pressed_cell_while_in_delete_mode = (empty_cell.mouse_on and UserControl.mouse_pressed[0] and state.gameplay.delete_mode and not state.gameplay.trains_released)
    if mouse_pressed_cell_while_in_delete_mode:
        empty_cell.tracks.clear()


def check_and_flip_cell_tracks(train: Train, cell: Cell) -> None:
    cell_contains_train_and_has_multiple_tracks = (cell.rect and cell.rect.contains(train.rect) and train.last_flipped_cell != cell and len(cell.tracks) == 2)
    if cell_contains_train_and_has_multiple_tracks and isinstance(cell, EmptyCell):
        cell.flip_tracks()
        train.last_flipped_cell = cell


def move_train_along_cell(train: Train, cell: Cell) -> None:
    if train.selected_track is None or cell.rect is None:
        return
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
                train.rect.center = cell.rect.midtop
                train.pos = pg.Vector2(train.rect.topleft)
        elif train.direction == Direction.DOWN:
            train.angle += Config.angular_vel
            if train.angle >= math.radians(360) - 0.5 * Config.angular_vel:
                train.direction = Direction.RIGHT
                train.angle = math.radians(0)
                train.rect.center = cell.rect.midright
                train.pos = pg.Vector2(train.rect.topleft)
    # If the selected track is top-left.
    elif train.selected_track.track_type == TrackType.TOP_LEFT:
        if train.direction == Direction.RIGHT:
            train.angle += Config.angular_vel
            if train.angle >= math.radians(90) - 0.5 * Config.angular_vel:
                train.direction = Direction.UP
                train.angle = math.radians(90)
                train.rect.center = cell.rect.midtop
                train.pos = pg.Vector2(train.rect.topleft)
        elif train.direction == Direction.DOWN:
            train.angle -= Config.angular_vel
            if train.angle <= math.radians(180) + 0.5 * Config.angular_vel:
                train.direction = Direction.LEFT
                train.angle = math.radians(180)
                train.rect.center = cell.rect.midleft
                train.pos = pg.Vector2(train.rect.topleft)
    # If the selected track is bottom-left.
    elif train.selected_track.track_type == TrackType.BOTTOM_LEFT:
        if train.direction == Direction.RIGHT:
            train.angle -= Config.angular_vel
            if train.angle <= math.radians(-90) + 0.5 * Config.angular_vel:
                train.direction = Direction.DOWN
                train.angle = math.radians(270)
                train.rect.center = cell.rect.midbottom
                train.pos = pg.Vector2(train.rect.topleft)
        elif train.direction == Direction.UP:
            train.angle += Config.angular_vel
            if train.angle >= math.radians(180) - 0.5 * Config.angular_vel:
                train.direction = Direction.LEFT
                train.angle = math.radians(180)
                train.rect.center = cell.rect.midleft
                train.pos = pg.Vector2(train.rect.topleft)
    # If the selected track is bottom-right.
    elif train.selected_track.track_type == TrackType.BOTTOM_RIGHT:
        if train.direction == Direction.LEFT:
            train.angle += Config.angular_vel
            if train.angle >= math.radians(270) - 0.5 * Config.angular_vel:
                train.direction = Direction.DOWN
                train.angle = math.radians(270)
                train.rect.center = cell.rect.midbottom
                train.pos = pg.Vector2(train.rect.topleft)
        elif train.direction == Direction.UP:
            train.angle -= Config.angular_vel
            if train.angle <= math.radians(0) + 0.5 * Config.angular_vel:
                train.direction = Direction.RIGHT
                train.angle = math.radians(0)
                train.rect.center = cell.rect.midright
                train.pos = pg.Vector2(train.rect.topleft)
    else:
        raise ValueError(f"Selected track type is {train.selected_track.track_type}")


def paint_trains(train_1: Train, train_2: Train) -> None:
    upcoming_color = blend_train_colors(train_1.color, train_2.color)
    train_1.repaint(upcoming_color)
    train_2.repaint(upcoming_color)
    Sound.play_sound_on_channel(Sound.merge, 0)


def merge_trains(train_1: Train, train_2: Train, field: Field) -> None:
    upcoming_train_color = blend_train_colors(train_1.color, train_2.color)
    train_1.repaint(upcoming_train_color)
    field.trains.remove(train_2)
    train_2.kill()
    logger.info(f"Removed a train! Trains remaining: {len(field.trains)} or {len(field.train_sprites)}") # type: ignore
    Sound.play_sound_on_channel(Sound.merge, 0)









def draw_middle_line(screen: Screen) -> None:
    pg.draw.line(screen.surface, WHITESMOKE, (screen.width / 2, 64), (screen.width / 2, 64 + 8 * 64))


def draw_background_basecolor(screen: Screen, state: State) -> None:
    if state.gameplay.trains_released:
        screen.surface.fill(DELETE_MODE_BG_COLOR)
    else:
        screen.surface.fill(NORMAL_MODE_BG_COLOR)


def draw_background_day_cycle(screen: Screen, state: State) -> None:
    state.gameplay.background_location = (-state.global_status.current_tick * Config.background_scroll_speed, 0)
    screen.surface.blit(Graphics.img_surfaces["day_cycle"], dest=state.gameplay.background_location)


def draw_station_goals(screen: Screen, field: Field) -> None:
    for arrival_station in field.arrival_stations:
        arrival_station.goal_sprites.draw(screen.surface) # type: ignore
    for departure_station in field.departure_stations:
        departure_station.goal_sprites.draw(screen.surface) # type: ignore


def draw_checkmarks(screen: Screen, field: Field) -> None:
    for arrival_station in field.arrival_stations:
        if arrival_station.checkmark is None or arrival_station.checkmark.image is None or arrival_station.rect is None:
            continue
        screen.surface.blit(source=arrival_station.checkmark.image, dest=arrival_station.rect.topleft)


def draw_empty_cells_tracks(screen: Screen, field: Field) -> None:
    for empty_cell in field.empty_cells:
        if empty_cell.rect is None:
            raise ValueError("The cell's rect is None. Exiting.")
        draw_empty_cell_tracks(screen, empty_cell)


def draw_arcs_and_endpoints(screen: Screen, track: Track):
    if track.bright:
        color = WHITE
    else:
        color = GRAY
    if track.track_type == TrackType.VERT:
        pg.draw.line(screen.surface, color, track.cell_rect.midtop, track.cell_rect.midbottom)
    elif track.track_type == TrackType.HORI:
        pg.draw.line(screen.surface, color, track.cell_rect.midleft, track.cell_rect.midright)
    elif track.track_type == TrackType.TOP_RIGHT:
        pygame.gfxdraw.arc(screen.surface, track.cell_rect.right, track.cell_rect.top, int(Config.cell_size / 2), 90, 180, color)
    elif track.track_type == TrackType.TOP_LEFT:
        pygame.gfxdraw.arc(screen.surface, track.cell_rect.left, track.cell_rect.top, int(Config.cell_size / 2), 0, 90, color)
    elif track.track_type == TrackType.BOTTOM_LEFT:
        pygame.gfxdraw.arc(screen.surface, track.cell_rect.left, track.cell_rect.bottom, int(Config.cell_size / 2), 270, 360, color)
    elif track.track_type == TrackType.BOTTOM_RIGHT:
        pygame.gfxdraw.arc(screen.surface, track.cell_rect.right, track.cell_rect.bottom, int(Config.cell_size / 2), 180, 270, color)

    for endpoint in track.endpoints:
        pygame.gfxdraw.pixel(screen.surface, int(endpoint.x), int(endpoint.y), RED1)


def draw_empty_cell_tracks(screen: Screen, empty_cell: EmptyCell) -> None:
    for track in empty_cell.tracks:
        if track.image:
            screen.surface.blit(track.image, dest=track.cell_rect)
        if Config.draw_arcs:
            draw_arcs_and_endpoints(screen, track)




def gameplay_phase(state: State, screen: Screen, field: Field) -> None:
    check_and_toggle_profiling(state)
    check_for_pygame_events(state, field)
    update_gameplay_state(state, field)
    check_and_save_field(field)
    reset_train_statuses(field)
    select_tracks_and_move_trains(state, field)
    check_and_delete_field_tracks(state, field)
    check_train_merges(field)
    check_train_arrivals(state, field)
    delete_crashed_trains(field)
    tick_trains(state, field)
    check_for_new_track_placement(state, field)
    check_for_level_completion(state, field)
    check_for_main_menu_command(state)
    tick_departures(state, field)
    determine_arrival_station_checkmarks(field)

    draw_background_basecolor(screen, state)
    draw_background_day_cycle(screen, state)
    field.empty_cells_sprites.draw(screen.surface)
    field.rock_cells_sprites.draw(screen.surface)
    draw_empty_cells_tracks(screen, field)
    field.train_sprites.draw(screen.surface)
    field.departure_stations_sprites.draw(screen.surface)
    field.arrival_stations_sprites.draw(screen.surface)
    draw_station_goals(screen, field)
    draw_middle_line(screen)
    draw_checkmarks(screen, field)





def main_menu_phase(state: State, screen: Screen, field: Field) -> None:
    UserControl.update_user_control_state()
    screen.surface.fill(GRAY10)
    check_for_pygame_events(state, field)
    check_for_gameplay_command(state)
    check_for_exit_command(state)


def exit_phase():
    logger.info("Exiting...")
    pg.quit()
    sys.exit()

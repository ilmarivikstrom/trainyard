import csv
import math
import random
from typing import List, Tuple, Union

import pygame as pg
import pygame.gfxdraw
from pygame.constants import (
    QUIT,
    MOUSEBUTTONDOWN,
    KEYDOWN,
    K_p,
    K_SPACE,
    K_UP,
    K_DOWN,
    K_F1,
)  # pylint: disable=no-name-in-module;

from src.cell import DrawingCell, RockCell
from src.color_constants import GRAY, RED1, WHITE, TRAIN_GREEN, TRAIN_RED, TRAIN_YELLOW
from src.config import Config
from src.user_control import UserControl
from src.direction import Direction, turn
from src.field import Field, TrackType
from src.menus import BuildPurgeMenu, EditTestMenu, LevelMenu, RunningCrashedCompleteMenu, InfoMenu
from src.state import Phase, State
from src.screen import Screen
from src.sound import Sound
from src.spark import Spark
from src.station import ArrivalStation, CheckmarkSprite, DepartureStation
from src.track import Track
from src.train import Train
from src.traincolor import blend_train_colors
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


build_purge_menu = BuildPurgeMenu(topleft=(64, 16))
edit_test_menu = EditTestMenu(topleft=(4 * 64, 16))
running_crashed_complete_menu = RunningCrashedCompleteMenu(topleft=(9 * 64, 16))
level_menu = LevelMenu(topleft=(12 * 64, 16), num_levels=10)  # Hardcoded number of levels (for now).
tick_menu = InfoMenu(topleft=(15 * 64, 16), tooltip_text="TICKS", value="")
track_menu = InfoMenu(topleft=(17 * 64, 16), tooltip_text="TRACKS", value="")
train_menu = InfoMenu(topleft=(17 * 64, 64), tooltip_text="TRAINS", value="")


def gameplay_phase(state: State, screen: Screen, field: Field) -> None:
    execute_logic(state, field)
    draw_game_objects(field, screen)


def execute_logic(state: State, field: Field) -> None:
    check_for_pg_gameplay_events()
    check_for_level_change(field)
    check_for_exit_command(state)
    check_and_set_delete_mode(state)
    check_and_save_field(field)
    check_and_toggle_profiling(state)
    check_and_toggle_train_release(field)
    check_and_reset_gameplay(state, field)

    check_and_flip_cell_tracks(field)  # if is_released: for cells, for trains
    check_for_track_flip_command(field)
    check_for_music_toggle_command()
    tick_departures(field)  # if is_released: for departure_stations
    check_train_departure_station_crashes(field)  # if is_released: for trains, for departure_stations
    delete_crashed_trains(field)  # if is_released: for trains
    select_tracks_for_trains(field)  # if is_released: for trains, for track, for endpoint
    check_train_arrivals(field)  # if is_released: for trains, for arrival_stations

    check_for_level_completion(state, field)  # if is_released
    check_train_merges(field)  # if is_released: for trains

    check_train_painters(field)
    check_train_splitters(field)

    check_and_mark_prev_cell(field)  # if NOT is_released: for cells (UserControl)
    check_and_delete_field_tracks(state, field)  # if NOT is_released: for drawing cells
    check_for_new_track_placement(state, field)  # if NOT is_released

    tick_trains(field)  # for trains

    check_for_mainmenu_command(state)
    determine_arrival_station_checkmarks(field)  # for arrival_stations
    tick_field(field)
    update_field_border(state, field)
    update_menu_indicators(state, field)

    update_sparks(field)


def draw_game_objects(field: Field, screen: Screen) -> None:
    draw_background_basecolor(screen)  # Background
    field.drawing_cells_sprites.draw(screen.surface)  # Empty cells (base).
    draw_drawing_cells_tracks(screen, field)  # Tracks (on empty cells).
    field.train_sprites.draw(screen.surface)  # Trains.
    field.rock_cells_sprites.draw(screen.surface)  # Rock cells.
    draw_stations(field, screen)  # Stations.
    field.painter_cells_sprites.draw(screen.surface)
    field.splitter_cells_sprites.draw(screen.surface)
    draw_field_border(field, screen)  # Field border.
    draw_menus(screen)  # Menus.

    draw_sparks(field, screen)


def check_train_splitters(field: Field) -> None:
    if field.current_tick == 0 or field.current_tick % 32 != 0:
        return
    trains_to_add: List[Train] = []
    for train in field.trains:
        for splitter in field.splitter_cells:
            if splitter.rect is None:
                raise ValueError("Rect is None.")
            if train.rect.center == splitter.rect.center:
                logger.info("At center.")
                new_train_1 = Train(
                    train.i, train.j, train.color, splitter.tracks[1], direction=turn(train.direction, left=True)
                )
                new_train_1.rect.x = train.rect.x
                new_train_1.rect.y = train.rect.y
                trains_to_add.append(new_train_1)
                train.selected_track = splitter.tracks[2]
                train.direction = turn(train.direction, right=True)
                train.angle = train.direction.value

    for new_train in trains_to_add:
        field.trains.append(new_train)
        field.train_sprites.add(new_train)


def check_train_painters(field: Field) -> None:
    for train in field.trains:
        for painter in field.painter_cells:
            if painter.rect is None:
                raise ValueError("Rect is None.")
            if train.rect.center == painter.rect.center:
                train.repaint(painter.color)


def draw_sparks(field: Field, screen: Screen) -> None:
    for spark in field.sparks:
        spark.draw(screen.surface)


def update_sparks(field: Field) -> None:
    solid_rects: List[pg.Rect] = []
    for item in field.full_grid:
        if item.rect is None:
            raise ValueError("Rect is None.")
        solid_types = Union[DepartureStation, ArrivalStation, RockCell]
        if isinstance(item, solid_types):
            solid_rects.append(item.rect)
    for i, spark in sorted(enumerate(field.sparks), reverse=True):
        spark.move(1, pg.Rect(64, 128, field.width_px, field.height_px), solid_rects)
        if not spark.alive:
            field.sparks.pop(i)


def generate_sparks(field: Field, pos: Tuple[int, int], angle: float) -> None:
    spark_colors = [(255, 207, 119), (254, 126, 5), (239, 99, 5), (177, 72, 3), (255, 237, 168)]
    for _ in range(random.randint(10, 30)):
        field.sparks.append(
            Spark(
                loc=(pos[0] + random.randint(-10, 10), pos[1] + random.randint(10, 10)),
                angle=math.radians(random.randint(-int(angle) - 70, -int(angle) + 70)),
                base_speed=random.uniform(1, 2),
                friction=random.uniform(0.01, 0.03),
                color=random.sample(spark_colors, 1)[0],
                scale=5.0,
                speed_multiplier=1.0,
            )
        )


def check_for_level_change(field: Field) -> None:
    for i, indicator_item in enumerate(level_menu.indicator_items):
        if indicator_item.activated:
            if i != field.level:
                field.load_level(i)


def draw_field_border(field: Field, screen: Screen) -> None:
    field.border.draw(screen.surface)


def draw_menus(screen: Screen) -> None:
    build_purge_menu.draw(screen.surface)
    edit_test_menu.draw(screen.surface)
    running_crashed_complete_menu.draw(screen.surface)
    level_menu.draw(screen.surface)
    tick_menu.draw(screen.surface)
    track_menu.draw(screen.surface)
    train_menu.draw(screen.surface)


def check_for_exit_command(state: State) -> None:
    for event in UserControl.events:
        if event.type == QUIT:
            state.game_phase = Phase.EXIT
            logger.info(f"Moving to phase {state.game_phase}")
            return


def check_for_track_flip_command(field: Field) -> None:
    for event in UserControl.events:
        if event.type == MOUSEBUTTONDOWN and event.button == 3:
            for drawing_cell in field.drawing_cells:
                if drawing_cell.mouse_on and not field.is_released and len(drawing_cell.tracks) > 1:
                    drawing_cell.flip_tracks()
            return


def check_for_music_toggle_command() -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == K_p:
            Sound.toggle_music(ms=500)
            return


def update_field_border(state: State, field: Field) -> None:
    if field.is_released:
        if field.num_crashed > 0:
            field.border.color = TRAIN_RED
        elif state.gameplay.current_level_passed:
            field.border.color = TRAIN_GREEN
        else:
            field.border.color = TRAIN_YELLOW
        return
    if state.gameplay.in_delete_mode:
        field.border.color = TRAIN_RED
    else:
        field.border.color = TRAIN_YELLOW


def update_menu_indicators(state: State, field: Field) -> None:
    update_build_purge_menu(state, field)
    update_edit_test_menu(field)
    update_running_crashed_complete_menu(state, field)
    update_level_menu()
    update_info_menu(field)
    update_track_menu(field)
    update_train_menu(field)


def update_train_menu(field: Field) -> None:
    train_menu.set_text(text=str(len(field.trains)), item_index=0)


def update_level_menu() -> None:
    activated_items = level_menu.get_activated_items()
    if len(activated_items) == 0:
        level_menu.activate_item(0)
        return
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == K_DOWN:
            level_menu.activate_next_item()
        elif event.type == KEYDOWN and event.key == K_UP:
            level_menu.activate_previous_item()


def update_build_purge_menu(state: State, field: Field) -> None:
    if state.gameplay.in_delete_mode:
        build_purge_menu.activate_item(1)
    else:
        build_purge_menu.activate_item(0)
    if field.is_released:
        build_purge_menu.deactivate_all()


def update_edit_test_menu(field: Field) -> None:
    if field.is_released:
        edit_test_menu.activate_item(1)
    else:
        edit_test_menu.activate_item(0)


def update_running_crashed_complete_menu(state: State, field: Field) -> None:
    if state.gameplay.current_level_passed:
        running_crashed_complete_menu.activate_item(2)
    elif field.num_crashed > 0:
        running_crashed_complete_menu.activate_item(1)
    elif field.is_released:
        running_crashed_complete_menu.activate_item(0)
    else:
        running_crashed_complete_menu.deactivate_all()


def update_info_menu(field: Field) -> None:
    tick_menu.set_text(text=str(int((field.current_tick - 32) / 64)), item_index=0)


def update_track_menu(field: Field) -> None:
    tracks = 0
    for item in field.full_grid:
        if isinstance(item, DrawingCell):
            tracks += len(item.tracks)
    track_menu.set_text(text=str(tracks), item_index=0)


def check_for_mainmenu_command(state: State) -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == UserControl.MAIN_MENU:
            state.game_phase = Phase.MAIN_MENU
            logger.info(f"Moving to phase {state.game_phase}")


def check_and_toggle_profiling(state: State) -> None:
    if UserControl.pressed_keys[K_F1]:
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


def check_train_merges(field: Field) -> None:
    if not field.is_released:
        return
    for train_1 in field.trains:
        other_trains = field.trains.copy()
        other_trains.remove(train_1)
        other_trains_pos = [(x.rect.centerx, x.rect.centery, 1, 1) for x in other_trains]
        collided_train_index = pg.Rect((train_1.rect.centerx, train_1.rect.centery, 2, 2)).collidelist(other_trains_pos)
        if collided_train_index == -1:
            continue
        train_2 = other_trains[collided_train_index]
        if train_1.direction == train_2.direction:
            merge_trains(train_1, train_2, field)
        else:
            paint_trains(train_1, train_2)


def delete_crashed_trains(field: Field) -> None:
    if not field.is_released:
        return
    for train in field.trains:
        if train.crashed:
            field.train_sprites.remove(train)  # type: ignore
            field.trains.remove(train)
            generate_sparks(field, (train.rect.centerx, train.rect.centery), train.angle)
            logger.info(f"Train crashed. Trains left: {len(field.trains)}")


def check_and_save_field(field: Field, file_name: str = "level_tmp.csv") -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == UserControl.SAVE_GAME:
            file_path = f"levels/{file_name}"
            with open(file_path, newline="", mode="w", encoding="utf-8") as level_file:
                level_writer = csv.writer(level_file, delimiter="-")
                row: List[str] = []
                for i, cell in enumerate(field.full_grid):
                    row.append(cell.saveable_attributes.serialize())
                    if (i + 1) % 8 == 0:
                        level_writer.writerow(row)
                        row.clear()
            logger.info(f"Saved game to '{file_path}'")


def check_and_set_delete_mode(state: State) -> None:
    if UserControl.pressed_keys[UserControl.DELETE_MODE]:
        state.gameplay.in_delete_mode = True
    else:
        state.gameplay.in_delete_mode = False


def reset_to_beginning(state: State, field: Field) -> None:
    field.reset()
    state.reset_gameplay_status()


def tick_trains(field: Field) -> None:
    for train in field.trains:
        train.tick(field.is_released)


def check_train_arrivals(field: Field) -> None:
    if not field.is_released:
        return
    for train in field.trains:
        for arrival_station in field.arrival_stations:
            if arrival_station.rect is None:
                raise ValueError(f"The rect of {arrival_station} is None.")
            if not train.rect.collidepoint(arrival_station.rect.center):
                continue
            if (
                train.color == arrival_station.train_color
                and arrival_station.goals
                and arrival_station.number_of_trains_left > 0
            ):
                field.trains.remove(train)
                field.train_sprites.remove(train)  # type: ignore
                arrival_station.number_of_trains_left -= 1
                arrival_station.goals.pop().kill()
                Sound.play_sound_on_any_channel(Sound.pop)
            else:
                logger.debug("CRASH! Wrong color train or not expecting further arrivals.")
                train.crash()
                field.num_crashed += 1
                arrival_station.checkmark = None


def tick_departures(field: Field) -> None:
    if not field.is_released:
        return
    for departure_station in field.departure_stations:
        res = departure_station.tick(field.current_tick)
        if res is not None:
            add_new_train(field, res)


def check_for_level_completion(state: State, field: Field) -> None:
    if (
        not state.gameplay.current_level_passed
        and not arrivals_pending(field)
        and field.num_crashed == 0
        and len(field.trains) == 0
        and field.is_released
    ):
        Sound.success.play()
        state.gameplay.current_level_passed = True


def check_for_new_track_placement(state: State, field: Field) -> None:
    left_mouse_down_in_draw_mode = (
        UserControl.mouse_pressed[0] and not state.gameplay.in_delete_mode and not field.is_released
    )

    if left_mouse_down_in_draw_mode and UserControl.prev_cell is not None and UserControl.mouse_entered_new_cell:
        mouse_moved_up_twice = UserControl.prev_movement == Direction.UP and UserControl.curr_movement == Direction.UP
        mouse_moved_down_twice = (
            UserControl.prev_movement == Direction.DOWN and UserControl.curr_movement == Direction.DOWN
        )
        mouse_moved_right_twice = (
            UserControl.prev_movement == Direction.RIGHT and UserControl.curr_movement == Direction.RIGHT
        )
        mouse_moved_left_twice = (
            UserControl.prev_movement == Direction.LEFT and UserControl.curr_movement == Direction.LEFT
        )
        moues_moved_upleft = UserControl.prev_movement == Direction.UP and UserControl.curr_movement == Direction.LEFT
        mouse_moved_rightdown = (
            UserControl.prev_movement == Direction.RIGHT and UserControl.curr_movement == Direction.DOWN
        )
        mouse_moved_upright = UserControl.prev_movement == Direction.UP and UserControl.curr_movement == Direction.RIGHT
        mouse_moved_leftdown = (
            UserControl.prev_movement == Direction.LEFT and UserControl.curr_movement == Direction.DOWN
        )
        mouse_moved_downright = (
            UserControl.prev_movement == Direction.DOWN and UserControl.curr_movement == Direction.RIGHT
        )
        mouse_moved_leftup = UserControl.prev_movement == Direction.LEFT and UserControl.curr_movement == Direction.UP
        mouse_moved_downleft = (
            UserControl.prev_movement == Direction.DOWN and UserControl.curr_movement == Direction.LEFT
        )
        mouse_moved_rightup = UserControl.prev_movement == Direction.RIGHT and UserControl.curr_movement == Direction.UP
        if mouse_moved_up_twice or mouse_moved_down_twice:
            field.insert_track_to_position(TrackType.VERT, UserControl.prev_cell)
            Sound.play_sound_on_any_channel(Sound.track_place)
        elif mouse_moved_right_twice or mouse_moved_left_twice:
            field.insert_track_to_position(TrackType.HORI, UserControl.prev_cell)
            Sound.play_sound_on_any_channel(Sound.track_place)
        elif moues_moved_upleft or mouse_moved_rightdown:
            field.insert_track_to_position(TrackType.BOTTOM_LEFT, UserControl.prev_cell)
            Sound.play_sound_on_any_channel(Sound.track_place)
        elif mouse_moved_upright or mouse_moved_leftdown:
            field.insert_track_to_position(TrackType.BOTTOM_RIGHT, UserControl.prev_cell)
            Sound.play_sound_on_any_channel(Sound.track_place)
        elif mouse_moved_downright or mouse_moved_leftup:
            field.insert_track_to_position(TrackType.TOP_RIGHT, UserControl.prev_cell)
            Sound.play_sound_on_any_channel(Sound.track_place)
        elif mouse_moved_downleft or mouse_moved_rightup:
            field.insert_track_to_position(TrackType.TOP_LEFT, UserControl.prev_cell)
            Sound.play_sound_on_any_channel(Sound.track_place)
        UserControl.mouse_entered_new_cell = False


def check_for_pg_gameplay_events() -> None:
    UserControl.update_user_events()


def select_tracks_for_trains(field: Field) -> None:
    if not field.is_released:
        return
    for train in field.trains:
        if train.selected_track is None:
            train.crash()
            field.num_crashed += 1
            continue
        if train.current_navigation_index == len(train.selected_track.navigation):
            train.last_flipped_cell = None  # Experimental.
            train.determine_next_cell_coords_and_direction()
            next_cell_tracks = field.get_grid_cell_at(train.next_cell_coords[0], train.next_cell_coords[1]).tracks
            if len(next_cell_tracks) == 0:
                train.crash()
                field.num_crashed += 1
                continue
            found_track = False
            for track in next_cell_tracks:
                for endpoint in track.endpoints:
                    if train.rect.collidepoint(endpoint):
                        found_track = True
                        train.selected_track = track
                        train.rect.centerx = int(endpoint[0])
                        train.rect.centery = int(endpoint[1])
            if not found_track:
                train.crash()
                field.num_crashed += 1
                continue
            train.current_navigation_index = 0
            train.direction = train.next_cell_direction
            train.next_cell_direction = Direction.NONE


def check_and_mark_prev_cell(field: Field) -> None:
    if field.is_released:
        return
    for cell in field.full_grid:
        if cell.check_mouse_collision():
            UserControl.mouse_entered_new_cell = True


def check_and_delete_field_tracks(state: State, field: Field) -> None:
    if field.is_released:
        return
    for drawing_cell in field.drawing_cells:
        if drawing_cell.rect is None:
            raise ValueError("The cell's rect is None. Exiting.")
        check_and_delete_drawing_cell_tracks(state, drawing_cell)


def add_new_train(field: Field, train: Train) -> None:
    field.trains.append(train)
    field.train_sprites.add(train)  # type: ignore


def check_and_delete_drawing_cell_tracks(state: State, drawing_cell: DrawingCell) -> None:
    mouse_pressed_cell_while_in_delete_mode = (
        drawing_cell.mouse_on and UserControl.mouse_pressed[0] and state.gameplay.in_delete_mode
    )
    if mouse_pressed_cell_while_in_delete_mode:
        drawing_cell.tracks.clear()


def check_and_flip_cell_tracks(field: Field) -> None:
    if not field.is_released:
        return
    for cell in field.full_grid:
        for train in field.trains:
            if train.current_navigation_index % 16 != 0:
                return
            cell_contains_train_and_has_multiple_tracks = (
                cell.rect
                and cell.rect.contains(train.rect)
                and train.current_navigation_index >= 23
                and train.last_flipped_cell != cell
                and len(cell.tracks) == 2
            )
            if cell_contains_train_and_has_multiple_tracks and isinstance(cell, DrawingCell):
                cell.flip_tracks()
                train.last_flipped_cell = cell


def paint_trains(train_1: Train, train_2: Train) -> None:
    upcoming_color = blend_train_colors(train_1.color, train_2.color)
    train_1.repaint(upcoming_color)
    train_2.repaint(upcoming_color)
    Sound.play_sound_on_any_channel(Sound.merge)


def merge_trains(train_1: Train, train_2: Train, field: Field) -> None:
    upcoming_train_color = blend_train_colors(train_1.color, train_2.color)
    train_1.repaint(upcoming_train_color)
    field.trains.remove(train_2)
    train_2.kill()
    logger.info(f"Removed a train! Trains remaining: {len(field.trains)} or {len(field.train_sprites)}")  # type: ignore
    Sound.play_sound_on_any_channel(Sound.merge)


def draw_background_basecolor(screen: Screen) -> None:
    tick_index = 300
    screen.surface.fill(screen.background_color_array[tick_index])


def draw_station_goals(screen: Screen, field: Field) -> None:
    for arrival_station in field.arrival_stations:
        arrival_station.goal_sprites.draw(screen.surface)  # type: ignore
    for departure_station in field.departure_stations:
        departure_station.goal_sprites.draw(screen.surface)  # type: ignore


def draw_checkmarks(screen: Screen, field: Field) -> None:
    for arrival_station in field.arrival_stations:
        if arrival_station.checkmark is None or arrival_station.checkmark.image is None or arrival_station.rect is None:
            continue
        screen.surface.blit(source=arrival_station.checkmark.image, dest=arrival_station.rect.topleft)


def draw_drawing_cells_tracks(screen: Screen, field: Field) -> None:
    for drawing_cell in field.drawing_cells:
        if drawing_cell.rect is None:
            raise ValueError("The cell's rect is None. Exiting.")
        draw_drawing_cell_tracks(screen, drawing_cell)


def draw_stations(field: Field, screen: Screen) -> None:
    field.departure_stations_sprites.draw(screen.surface)
    field.arrival_stations_sprites.draw(screen.surface)
    draw_station_goals(screen, field)
    draw_checkmarks(screen, field)


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
        pygame.gfxdraw.arc(
            screen.surface, track.cell_rect.right, track.cell_rect.top, int(Config.cell_size / 2), 90, 180, color
        )
    elif track.track_type == TrackType.TOP_LEFT:
        pygame.gfxdraw.arc(
            screen.surface, track.cell_rect.left, track.cell_rect.top, int(Config.cell_size / 2), 0, 90, color
        )
    elif track.track_type == TrackType.BOTTOM_LEFT:
        pygame.gfxdraw.arc(
            screen.surface, track.cell_rect.left, track.cell_rect.bottom, int(Config.cell_size / 2), 270, 360, color
        )
    elif track.track_type == TrackType.BOTTOM_RIGHT:
        pygame.gfxdraw.arc(
            screen.surface, track.cell_rect.right, track.cell_rect.bottom, int(Config.cell_size / 2), 180, 270, color
        )

    for endpoint in track.endpoints:
        pygame.gfxdraw.pixel(screen.surface, int(endpoint.x), int(endpoint.y), RED1)


def draw_drawing_cell_tracks(screen: Screen, drawing_cell: DrawingCell) -> None:
    for track in drawing_cell.tracks:
        if track.image:
            screen.surface.blit(track.image, dest=track.cell_rect)
        if Config.draw_arcs:
            draw_arcs_and_endpoints(screen, track)


def check_and_reset_gameplay(state: State, field: Field) -> None:
    if not field.is_released:
        reset_to_beginning(state, field)


def tick_field(field: Field) -> None:
    field.set_current_tick()


def check_train_departure_station_crashes(field: Field) -> None:
    if not field.is_released:
        return
    for train in field.trains:
        for departure_station in field.departure_stations:
            if departure_station.rect is None:
                raise ValueError("Rect is None.")
            if departure_station.rect.collidepoint(train.rect.center) and train.angle != departure_station.angle:
                train.crash()
                field.num_crashed += 1


def check_and_toggle_train_release(field: Field) -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == K_SPACE:
            field.is_released = not field.is_released

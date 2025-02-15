"""Phase: Gameplay."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

import pygame as pg
import pygame.gfxdraw
from pygame.constants import (
    K_DOWN,
    K_F1,
    K_SPACE,
    K_UP,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    QUIT,
    K_m,
    K_n,
    K_p,
)

from src.cell import DrawingCell, RockCell
from src.color_constants import GRAY, RED1, TY_GREEN, TY_RED, TY_TELLOW, WHITE
from src.config import Config
from src.direction import Direction, turn
from src.field import Field, TrackType
from src.graphics import Graphics
from src.levelitems.painter import Painter
from src.levelitems.splitter import Splitter
from src.levelitems.station import (
    ArrivalStation,
    CheckmarkSprite,
    DepartureStation,
)
from src.menus.menus import (
    BuildPurgeMenu,
    EditTestMenu,
    InfoMenu,
    LevelMenu,
    RunningCrashedCompleteMenu,
)
from src.screen import Screen
from src.sound import Sound
from src.spark import (
    CircleCloudShape,
    FastSmallShortLivedSpark,
    FlameSparkStyle,
    SlowLargeSpark,
    SparkCloud,
    WeldingSparkStyle,
    WideConeCloudShape,
)
from src.state import Phase, State
from src.train import Train
from src.traincolor import blend_train_colors
from src.user_control import UserControl
from src.utils.utils import setup_logging

if TYPE_CHECKING:
    from src.levelitems.painter import Painter
    from src.levelitems.splitter import Splitter
    from src.screen import Screen
    from src.track import Track

logger = setup_logging(log_level=Config.log_level)


build_purge_menu = BuildPurgeMenu(topleft=(1 * 64, 16))
edit_test_menu = EditTestMenu(topleft=(5 * 64, 16))
running_crashed_complete_menu = RunningCrashedCompleteMenu(topleft=(10 * 64, 16))
level_menu = LevelMenu(
    topleft=(13 * 64, 16),
    num_levels=6,
)  # Hardcoded number of levels (for now).
track_menu = InfoMenu(topleft=(1 * 64, 10 * 64 + 16), tooltip_text="TRACKS", value="")
tick_menu = InfoMenu(topleft=(3 * 64, 10 * 64 + 16), tooltip_text="TICKS", value="")
train_menu = InfoMenu(topleft=(5 * 64, 10 * 64 + 16), tooltip_text="TRAINS", value="")
crash_menu = InfoMenu(topleft=(7 * 64, 10 * 64 + 16), tooltip_text="CRASHES", value="")
spark_menu = InfoMenu(topleft=(9 * 64, 10 * 64 + 16), tooltip_text="SPARKS", value="")
music_menu = InfoMenu(
    topleft=(10 * 64, 9 * 64 + 16),
    tooltip_text="MUSIC (P)",
    value="",
)


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

    check_for_next_music_command()

    check_and_flip_cell_tracks(field)  # if is_released: for cells, for trains
    check_for_track_flip_command(field)
    check_for_music_toggle_command()
    tick_departures(field)  # if is_released: for departure_stations
    check_train_departure_station_crashes(
        field,
    )  # if is_released: for trains, for departure_stations
    select_tracks_for_trains(
        field,
    )  # if is_released: for trains, for track, for endpoint
    delete_crashed_trains(field)  # if is_released: for trains
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

    update_all_sparks(field)


def draw_game_objects(field: Field, screen: Screen) -> None:
    draw_background_basecolor(screen)  # Background
    field.grid.drawing_cells.sprites.draw(screen.surface)  # Empty cells (base).
    draw_drawing_cells_tracks(screen, field)  # Tracks (on empty cells).
    field.grid.trains.sprites.draw(screen.surface)  # Trains.
    field.grid.rocks.sprites.draw(screen.surface)

    draw_stations(field, screen)  # Stations.
    field.grid.painters.sprites.draw(screen.surface)
    field.grid.splitters.sprites.draw(screen.surface)
    draw_field_border(field, screen)  # Field border.
    draw_menus(screen)  # Menus.

    draw_crash_sparks(field, screen)  # Crash sparks.


def check_train_splitters(field: Field) -> None:
    if field.current_tick == 0 or field.current_tick % 32 != 0:
        return
    trains_to_add: list[Train] = []
    for train in field.grid.trains.items:
        for splitter in field.grid.splitters.items:
            if train.rect.center == splitter.rect.center:
                logger.info("At center.")
                new_train_1 = Train(
                    train.loc,
                    train.color,
                    splitter.cell_tracks[1],
                    direction=turn(train.direction, left=True),
                )
                new_train_1.rect.x = train.rect.x
                new_train_1.rect.y = train.rect.y
                trains_to_add.append(new_train_1)
                train.selected_track = splitter.cell_tracks[2]
                train.direction = turn(train.direction, right=True)
                train.angle = train.direction.value
                Sound.play_sound_on_any_channel(Sound.pop)

    for new_train in trains_to_add:
        field.grid.trains.items.append(new_train)
        field.grid.trains.sprites.add(new_train)


def check_train_painters(field: Field) -> None:
    for train in field.grid.trains.items:
        for painter in field.grid.painters.items:
            if train.rect.center == painter.rect.center:
                train.repaint(painter.color)


def draw_crash_sparks(field: Field, screen: Screen) -> None:
    for spark in field.sparks:
        spark.draw(screen.surface)


def get_solid_cells(
    field: Field,
) -> list[
    ArrivalStation | DepartureStation | Painter | RockCell | Splitter
]:  # TODO: Store solid cells in some structure instead of getting them every loop.
    solid_cells: list[
        ArrivalStation | DepartureStation | Painter | RockCell | Splitter
    ] = []
    solid_cells.extend(field.grid.arrivals.items)
    solid_cells.extend(field.grid.departures.items)
    solid_cells.extend(field.grid.painters.items)
    solid_cells.extend(field.grid.rocks.items)
    solid_cells.extend(field.grid.splitters.items)
    return solid_cells


def update_all_sparks(field: Field) -> None:
    solid_items = get_solid_cells(field)
    solid_rects: list[pg.Rect] = [solid_item.rect for solid_item in solid_items]
    for i, spark in sorted(enumerate(field.sparks), reverse=True):
        spark.move(1, pg.Rect(64, 128, field.width_px, field.height_px), solid_rects)
        if not spark.alive:
            field.sparks.pop(i)


def generate_crash_sparks(field: Field, pos: tuple[int, int], angle: float) -> None:
    spark_cloud = SparkCloud(
        pos=pos,
        shape=WideConeCloudShape(angle),
        pos_deviation=(10, 10),
        style=FlameSparkStyle(),
        behavior=SlowLargeSpark(),
        spark_count=20,
        spark_count_deviation=10,
    )
    sparks = spark_cloud.emit_sparks()
    for spark in sparks:
        field.sparks.append(spark)


def generate_track_insert_sparks(field: Field, pos: tuple[int, int]) -> None:
    spark_cloud = SparkCloud(
        pos=pos,
        shape=CircleCloudShape(0.0),
        pos_deviation=(10, 10),
        style=WeldingSparkStyle(),
        behavior=FastSmallShortLivedSpark(),
        spark_count=10,
        spark_count_deviation=2,
    )
    sparks = spark_cloud.emit_sparks()
    for spark in sparks:
        field.sparks.append(spark)


def check_for_level_change(field: Field) -> None:
    for i, indicator_item in enumerate(level_menu.indicator_items):
        if indicator_item.activated and i != field.level:
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
    crash_menu.draw(screen.surface)
    spark_menu.draw(screen.surface)
    music_menu.draw(screen.surface)


def check_for_exit_command(state: State) -> None:
    for event in UserControl.events:
        if event.type == QUIT:
            state.game_phase = Phase.EXIT
            logger.info(f"Moving to phase {state.game_phase}")
            return


def check_for_next_music_command() -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN:
            if event.key == K_n:
                Sound.init_music(song_name="Song 1")
                Sound.play_music()
            elif event.key == K_m:
                Sound.init_music(song_name="Song 9")
                Sound.play_music()


def check_for_track_flip_command(field: Field) -> None:
    for event in UserControl.events:
        if event.type == MOUSEBUTTONDOWN and event.button == 3:
            for drawing_cell in field.grid.drawing_cells.items:
                if (
                    drawing_cell.mouse_on
                    and not field.is_released
                    and len(drawing_cell.cell_tracks) > 1
                ):
                    drawing_cell.flip_tracks()
            return


def check_for_music_toggle_command() -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == K_p:
            Sound.toggle_music(ms=500)
            Config.play_music = not Config.play_music
            return


def update_field_border(state: State, field: Field) -> None:
    if field.is_released:
        if field.num_crashed > 0:
            field.border.color = TY_RED
        elif state.gameplay.current_level_passed:
            field.border.color = TY_GREEN
        else:
            field.border.color = TY_TELLOW
        return
    if state.gameplay.in_delete_mode:
        field.border.color = TY_RED
    else:
        field.border.color = TY_TELLOW


def update_menu_indicators(state: State, field: Field) -> None:
    update_build_purge_menu(state, field)
    update_edit_test_menu(field)
    update_running_crashed_complete_menu(state, field)
    update_level_menu()
    update_info_menu(field)
    update_track_menu(field)
    update_train_menu(field)
    update_crash_menu(field)
    update_spark_menu(field)
    update_music_menu()


def update_train_menu(field: Field) -> None:
    train_menu.set_text(text=str(len(field.grid.trains.items)), item_index=0)


def update_spark_menu(field: Field) -> None:
    spark_menu.set_text(text=str(len(field.sparks)), item_index=0)


def update_crash_menu(field: Field) -> None:
    crash_menu.set_text(text=str(field.num_crashed), item_index=0)


def update_music_menu() -> None:
    play_music_text = "OFF"
    if Sound.music_playing:
        play_music_text = "ON"
    music_menu.set_text(text=play_music_text, item_index=0)


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
    running_crashed_complete_menu.mouse_on(UserControl.mouse_pos)


def update_info_menu(field: Field) -> None:
    tick_menu.set_text(text=str(int((field.current_tick - 32) / 64)), item_index=0)


def update_track_menu(field: Field) -> None:
    tracks = 0
    for item in field.grid.all_items:
        if isinstance(item, DrawingCell):
            tracks += len(item.cell_tracks)
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
    for arrival_station in field.grid.arrivals.items:
        if arrival_station.number_of_trains_left == 0:
            arrival_station.checkmark = CheckmarkSprite(arrival_station.rect)


def arrivals_pending(field: Field) -> bool:
    for arrival_station in field.grid.arrivals.items:
        if arrival_station.number_of_trains_left > 0:
            return True
    return False


def check_train_merges(field: Field) -> None:
    if not field.is_released:
        return
    for train_1 in field.grid.trains.items:
        other_trains = field.grid.trains.items.copy()
        other_trains.remove(train_1)
        other_trains_pos = [
            (x.rect.centerx, x.rect.centery, 1, 1) for x in other_trains
        ]
        collided_train_index = pg.Rect(
            (train_1.rect.centerx, train_1.rect.centery, 2, 2),
        ).collidelist(other_trains_pos)
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
    trains_to_remove: list[Train] = [
        train for train in field.grid.trains.items if train.crashed
    ]
    for train in trains_to_remove:
        field.grid.trains.sprites.remove(train)
        field.grid.trains.items.remove(train)
        generate_crash_sparks(
            field,
            (train.rect.centerx, train.rect.centery),
            train.angle,
        )
        logger.info(f"Train crashed. Trains left: {len(field.grid.trains.items)}")


def check_and_save_field(field: Field, file_name: str = "level_tmp.csv") -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == UserControl.SAVE_GAME:
            file_path = f"assets/levels/{file_name}"
            with open(file_path, newline="", mode="w", encoding="utf-8") as level_file:
                level_writer = csv.writer(level_file, delimiter="-")
                row: list[str] = []
                for i, cell in enumerate(field.grid.all_items):
                    row.append(cell.saveable_attributes.serialize())
                    if (i + 1) % 8 == 0:
                        level_writer.writerow(row)
                        row.clear()
            logger.info(f"Saved game to '{file_path}'")


def check_and_set_delete_mode(state: State) -> None:
    if (
        UserControl.pressed_keys[UserControl.DELETE_MODE_1]
        or UserControl.pressed_keys[UserControl.DELETE_MODE_2]
    ):
        state.gameplay.in_delete_mode = True
    else:
        state.gameplay.in_delete_mode = False


def reset_to_beginning(state: State, field: Field) -> None:
    field.reset()
    state.reset_gameplay_status()


def tick_trains(field: Field) -> None:
    if field.is_released:
        for train in field.grid.trains.items:
            train.tick()
    else:
        for train in field.grid.trains.items:
            train.reset()


def check_train_arrivals(field: Field) -> None:
    if not field.is_released:
        return
    for train in field.grid.trains.items:
        for arrival_station in field.grid.arrivals.items:
            if not train.rect.collidepoint(arrival_station.rect.center):
                continue
            if (
                train.color == arrival_station.train_color
                and arrival_station.goals
                and arrival_station.number_of_trains_left > 0
            ):
                field.grid.trains.remove_one(train)
                arrival_station.number_of_trains_left -= 1
                arrival_station.goals.pop().kill()
                Sound.play_sound_on_any_channel(Sound.pop)
            else:
                logger.debug(
                    "CRASH! Wrong color train or not expecting further arrivals.",
                )
                train.crash()
                field.num_crashed += 1
                arrival_station.checkmark = None


def tick_departures(field: Field) -> None:
    if not field.is_released:
        return
    for departure_station in field.grid.departures.items:
        res = departure_station.tick(field.current_tick)
        if res is not None:
            add_new_train(field, res)


def check_for_level_completion(state: State, field: Field) -> None:
    if (
        not state.gameplay.current_level_passed
        and not arrivals_pending(field)
        and field.num_crashed == 0
        and len(field.grid.trains.items) == 0
        and field.is_released
    ):
        Sound.success.play()
        state.gameplay.current_level_passed = True


def check_for_new_track_placement(state: State, field: Field) -> None:
    left_mouse_down_in_draw_mode = (
        UserControl.mouse_pressed[0]
        and not state.gameplay.in_delete_mode
        and not field.is_released
    )

    if (
        left_mouse_down_in_draw_mode
        and UserControl.prev_cell is not None
        and UserControl.mouse_entered_new_cell
    ):
        mouse_moved_up_twice = (
            UserControl.prev_movement == Direction.UP
            and UserControl.curr_movement == Direction.UP
        )
        mouse_moved_down_twice = (
            UserControl.prev_movement == Direction.DOWN
            and UserControl.curr_movement == Direction.DOWN
        )
        mouse_moved_right_twice = (
            UserControl.prev_movement == Direction.RIGHT
            and UserControl.curr_movement == Direction.RIGHT
        )
        mouse_moved_left_twice = (
            UserControl.prev_movement == Direction.LEFT
            and UserControl.curr_movement == Direction.LEFT
        )
        moues_moved_upleft = (
            UserControl.prev_movement == Direction.UP
            and UserControl.curr_movement == Direction.LEFT
        )
        mouse_moved_rightdown = (
            UserControl.prev_movement == Direction.RIGHT
            and UserControl.curr_movement == Direction.DOWN
        )
        mouse_moved_upright = (
            UserControl.prev_movement == Direction.UP
            and UserControl.curr_movement == Direction.RIGHT
        )
        mouse_moved_leftdown = (
            UserControl.prev_movement == Direction.LEFT
            and UserControl.curr_movement == Direction.DOWN
        )
        mouse_moved_downright = (
            UserControl.prev_movement == Direction.DOWN
            and UserControl.curr_movement == Direction.RIGHT
        )
        mouse_moved_leftup = (
            UserControl.prev_movement == Direction.LEFT
            and UserControl.curr_movement == Direction.UP
        )
        mouse_moved_downleft = (
            UserControl.prev_movement == Direction.DOWN
            and UserControl.curr_movement == Direction.LEFT
        )
        mouse_moved_rightup = (
            UserControl.prev_movement == Direction.RIGHT
            and UserControl.curr_movement == Direction.UP
        )
        did_insert = False
        if mouse_moved_up_twice or mouse_moved_down_twice:
            did_insert = field.insert_track_to_position(
                TrackType.VERT,
                UserControl.prev_cell,
            )
        elif mouse_moved_right_twice or mouse_moved_left_twice:
            did_insert = field.insert_track_to_position(
                TrackType.HORI,
                UserControl.prev_cell,
            )
        elif moues_moved_upleft or mouse_moved_rightdown:
            did_insert = field.insert_track_to_position(
                TrackType.BOTTOM_LEFT,
                UserControl.prev_cell,
            )
        elif mouse_moved_upright or mouse_moved_leftdown:
            did_insert = field.insert_track_to_position(
                TrackType.BOTTOM_RIGHT,
                UserControl.prev_cell,
            )
        elif mouse_moved_downright or mouse_moved_leftup:
            did_insert = field.insert_track_to_position(
                TrackType.TOP_RIGHT,
                UserControl.prev_cell,
            )
        elif mouse_moved_downleft or mouse_moved_rightup:
            did_insert = field.insert_track_to_position(
                TrackType.TOP_LEFT,
                UserControl.prev_cell,
            )
        if did_insert:
            Sound.play_sound_on_any_channel(Sound.track_place)
            drawing_cell = field.get_drawing_cell_at_pos(UserControl.prev_cell)
            if drawing_cell is not None:
                generate_track_insert_sparks(
                    field,
                    drawing_cell.rect.center,
                )
        UserControl.mouse_entered_new_cell = False


def check_for_pg_gameplay_events() -> None:
    UserControl.update_user_events()


def select_tracks_for_trains(field: Field) -> None:
    if not field.is_released:
        return
    for train in field.grid.trains.items:
        if train.selected_track is None:
            train.crash()
            field.num_crashed += 1
            continue
        if train.current_navigation_index == len(train.selected_track.navigation):
            train.last_flipped_cell = None  # Experimental.
            train.determine_next_cell_coords_and_direction()
            next_cell_tracks: list[Track] = field.get_grid_cell_at(
                train.next_cell_coords[0],
                train.next_cell_coords[1],
            ).cell_tracks
            if len(next_cell_tracks) == 0:
                train.crash()
                field.num_crashed += 1
                continue
            found_track = False
            for track in next_cell_tracks:
                for endpoint in track.endpoints:
                    if train.rect.collidepoint(endpoint.as_tuple_int()):
                        found_track = True
                        train.selected_track = track
                        train.rect.center = endpoint.as_tuple_int()
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
    for cell in field.grid.all_items:
        if cell.check_mouse_collision():
            UserControl.mouse_entered_new_cell = True


def check_and_delete_field_tracks(state: State, field: Field) -> None:
    if field.is_released:
        return
    for drawing_cell in field.grid.drawing_cells.items:
        check_and_delete_drawing_cell_tracks(state, drawing_cell)


def add_new_train(field: Field, train: Train) -> None:
    field.grid.trains.items.append(train)
    field.grid.trains.sprites.add(train)


def check_and_delete_drawing_cell_tracks(
    state: State,
    drawing_cell: DrawingCell,
) -> None:
    mouse_pressed_cell_while_in_delete_mode = (
        drawing_cell.mouse_on
        and UserControl.mouse_pressed[0]
        and state.gameplay.in_delete_mode
    )
    if mouse_pressed_cell_while_in_delete_mode:
        drawing_cell.cell_tracks.clear()


def check_and_flip_cell_tracks(field: Field) -> None:
    if not field.is_released:
        return
    for cell in field.grid.all_items:
        for train in field.grid.trains.items:
            if train.current_navigation_index % 16 != 0:
                return
            cell_contains_train_and_has_multiple_tracks = (
                cell.rect
                and cell.rect.contains(train.rect)
                and train.current_navigation_index >= 23  # Over halfway.
                and train.last_flipped_cell != cell
                and len(cell.cell_tracks) == 2
            )
            if cell_contains_train_and_has_multiple_tracks and isinstance(
                cell,
                DrawingCell,
            ):
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
    field.grid.trains.items.remove(train_2)
    train_2.kill()
    logger.info(
        f"Removed a train! Trains remaining: {len(field.grid.trains.items)}"
        " or {len(field.grid.trains.sprites)}",
    )
    Sound.play_sound_on_any_channel(Sound.merge)


def draw_background_basecolor(screen: Screen) -> None:
    screen.surface.blit(Graphics.img_surfaces["bg"], dest=(0, 0))


def draw_station_goals(screen: Screen, field: Field) -> None:
    for arrival_station in field.grid.arrivals.items:
        arrival_station.goal_sprites.draw(screen.surface)
    for departure_station in field.grid.departures.items:
        departure_station.goal_sprites.draw(screen.surface)


def draw_checkmarks(screen: Screen, field: Field) -> None:
    for arrival_station in field.grid.arrivals.items:
        if arrival_station.checkmark is None or arrival_station.checkmark.image is None:
            continue
        screen.surface.blit(
            source=arrival_station.checkmark.image,
            dest=arrival_station.rect.topleft,
        )


def draw_drawing_cells_tracks(screen: Screen, field: Field) -> None:
    for drawing_cell in field.grid.drawing_cells.items:
        draw_drawing_cell_tracks(screen, drawing_cell)


def draw_stations(field: Field, screen: Screen) -> None:
    field.grid.departures.sprites.draw(screen.surface)
    field.grid.arrivals.sprites.draw(screen.surface)
    draw_station_goals(screen, field)
    draw_checkmarks(screen, field)


def draw_arcs_and_endpoints(screen: Screen, track: Track) -> None:
    color = WHITE if track.bright else GRAY
    if track.track_type == TrackType.VERT:
        pg.draw.line(
            screen.surface,
            color,
            track.cell_rect.midtop,
            track.cell_rect.midbottom,
        )
    elif track.track_type == TrackType.HORI:
        pg.draw.line(
            screen.surface,
            color,
            track.cell_rect.midleft,
            track.cell_rect.midright,
        )
    elif track.track_type == TrackType.TOP_RIGHT:
        pygame.gfxdraw.arc(
            screen.surface,
            track.cell_rect.right,
            track.cell_rect.top,
            int(Config.cell_size / 2),
            90,
            180,
            color,
        )
    elif track.track_type == TrackType.TOP_LEFT:
        pygame.gfxdraw.arc(
            screen.surface,
            track.cell_rect.left,
            track.cell_rect.top,
            int(Config.cell_size / 2),
            0,
            90,
            color,
        )
    elif track.track_type == TrackType.BOTTOM_LEFT:
        pygame.gfxdraw.arc(
            screen.surface,
            track.cell_rect.left,
            track.cell_rect.bottom,
            int(Config.cell_size / 2),
            270,
            360,
            color,
        )
    elif track.track_type == TrackType.BOTTOM_RIGHT:
        pygame.gfxdraw.arc(
            screen.surface,
            track.cell_rect.right,
            track.cell_rect.bottom,
            int(Config.cell_size / 2),
            180,
            270,
            color,
        )

    for endpoint in track.endpoints:
        pygame.gfxdraw.pixel(screen.surface, int(endpoint.x), int(endpoint.y), RED1)


def draw_drawing_cell_tracks(screen: Screen, drawing_cell: DrawingCell) -> None:
    for track in drawing_cell.cell_tracks:
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
    for train in field.grid.trains.items:
        for departure_station in field.grid.departures.items:
            if (
                departure_station.rect.collidepoint(train.rect.center)
                and train.angle != departure_station.angle
            ):
                train.crash()
                field.num_crashed += 1


def check_and_toggle_train_release(field: Field) -> None:
    for event in UserControl.events:
        if event.type == KEYDOWN and event.key == K_SPACE:
            field.is_released = not field.is_released

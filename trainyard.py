import pygame as pg

from src.color_constants import TRAIN_RED, TRAIN_GREEN, TRAIN_YELLOW, GRAY5, GRAY10, GRAY20, GRAY30, GRAY40, GRAY50, GRAY60, GRAY70, GRAY80, WHITE, WHITESMOKE
from src.config import Config
from src.field import Field
from src.state import Phase, State
from src.phase_exit import exit_phase
from src.phase_gameplay import gameplay_phase
from src.phase_mainmenu import mainmenu_phase
from src.graphics import Graphics
from src.menuitem import MenuItem
from src.screen import Screen
from src.sound import Sound
from src.text import Text
from src.traincolor import TrainColor
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


def initial_pygame_setup():
    pg.display.set_caption("trainyard")
    Graphics.load_resources()


def main() -> None:
    screen = Screen()
    initial_pygame_setup()
    state = State()
    field = Field()
    field.initialize_grid()
    clock = pg.time.Clock()

    font = Text.get_font_with_size(16)
    font_small = Text.get_font_with_size(10)

    if Config.play_music:
        Sound.play_music()

    rect_color = TRAIN_YELLOW

    build_purge_tooltip = font_small.render("L-SHIFT", True, WHITE)
    build_purge_tooltip_dest = (1 * 64 + 32, 16 + 0)
    build_indicator = MenuItem(font, "BUILD", 2, GRAY5, TRAIN_YELLOW, (1 * 64 + 0,  16 + 20))
    purge_indicator = MenuItem(font, "PURGE", 2, GRAY5, TRAIN_RED, (1 * 64 + 0,  16 + 40))


    edit_run_tooltip = font_small.render("SPACEBAR", True, WHITE)
    edit_run_tooltip_dest =  (4 * 64 + 96, 16 + 0)
    edit_mode_indicator = MenuItem(font, "EDIT", 3, GRAY5, WHITESMOKE, (4 * 64 + 0,  16 + 20))
    run_mode_indicator = MenuItem(font, "TEST", 3, GRAY5, WHITESMOKE, (4 * 64 + 136,  16 + 20))


    running_crashed_complete_tooltip = font_small.render("LEVEL STATUS", True, WHITE)
    running_crashed_complete_tooltip_dest = (9 * 64 + 36, 16 + 0)
    running_status_indicator = MenuItem(font, "RUNNING", 3, GRAY5, TRAIN_YELLOW, (9 * 64 + 0, 16 + 20))
    crashed_indicator = MenuItem(font, "CRASHED", 3, GRAY5, TRAIN_RED, (9 * 64 + 0,  16 + 40))
    complete_indicator = MenuItem(font, "COMPLETE", 3, GRAY5, TRAIN_GREEN, (9 * 64 + 0,  16 + 60))


    while True:
        state.global_status.current_tick += 1
        if state.game_phase == Phase.MAIN_MENU:
            mainmenu_phase(state, screen)
        elif state.game_phase == Phase.EXIT:
            exit_phase()
        elif state.game_phase == Phase.GAMEPLAY:
            gameplay_phase(state, screen, field)


            # Calculate number of brown trains. Should be in field ticking.
            num_brown_trains = 0
            for train in field.trains:
                if train.color == TrainColor.BROWN:
                    num_brown_trains += 1


            # Build/Purge and delete mode.
            if state.gameplay.in_delete_mode:
                build_indicator.deactivate()
                purge_indicator.activate()
                rect_color = TRAIN_RED
            else:
                build_indicator.activate()
                purge_indicator.deactivate()
                rect_color = TRAIN_YELLOW


            # Build/Purge and is_released.
            if field.is_released:
                build_indicator.deactivate()
                purge_indicator.deactivate()


            # Edit/Run and is_released.
            if field.is_released:
                edit_mode_indicator.deactivate()
                run_mode_indicator.activate()
            else:
                edit_mode_indicator.activate()
                run_mode_indicator.deactivate()


            # Running/Crashed/Complete upon crashes, level passing, is_released.
            if state.gameplay.current_level_passed:
                running_status_indicator.deactivate()
                crashed_indicator.deactivate()
                complete_indicator.activate()
                rect_color = TRAIN_GREEN
            elif field.num_crashed > 0:
                running_status_indicator.deactivate()
                crashed_indicator.activate()
                complete_indicator.deactivate()
                rect_color = TRAIN_RED
            elif field.is_released:
                running_status_indicator.activate()
                crashed_indicator.deactivate()
                complete_indicator.deactivate()
                rect_color = TRAIN_YELLOW
            else:
                running_status_indicator.deactivate()
                crashed_indicator.deactivate()
                complete_indicator.deactivate()


            # Blitting all menu items in the end.
            screen.surface.blit(build_purge_tooltip, dest=build_purge_tooltip_dest)
            screen.surface.blit(build_indicator.rendered, dest=build_indicator.dest)
            screen.surface.blit(purge_indicator.rendered, dest=purge_indicator.dest)

            screen.surface.blit(edit_run_tooltip, dest=edit_run_tooltip_dest)
            screen.surface.blit(edit_mode_indicator.rendered, dest=edit_mode_indicator.dest)
            screen.surface.blit(run_mode_indicator.rendered, dest=run_mode_indicator.dest)

            screen.surface.blit(running_crashed_complete_tooltip, dest=running_crashed_complete_tooltip_dest)
            screen.surface.blit(running_status_indicator.rendered, dest=running_status_indicator.dest)
            screen.surface.blit(crashed_indicator.rendered, dest=crashed_indicator.dest)
            screen.surface.blit(complete_indicator.rendered, dest=complete_indicator.dest)


            # Displaying field border with 1 width.
            field_border = pg.Surface((512 + 2 * 1, 512 + 2 * 1), pg.SRCALPHA)
            pg.draw.rect(field_border, rect_color, (0, 0, 512 + 2 * 1, 512 + 2 * 1), 1)
            screen.surface.blit(field_border, (64 - 1 * 1, 128 - 1 * 1))

        pg.display.update()
        clock.tick(Config.FPS)



if __name__ == "__main__":
    main()

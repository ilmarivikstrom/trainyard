import pygame
from configparser import ConfigParser
from src.phases import exit_phase, gameplay_phase, main_menu_phase
from src.global_state import GameStatus, GlobalState
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")
config = ConfigParser()
config.read("config.ini")

pygame.init()


def main():
    pygame.display.set_caption("trainyard")
    screen_surface = pygame.display.set_mode(
        (int(config["SCREEN"]["WIDTH"]), int(config["SCREEN"]["HEIGHT"]))
    )
    GlobalState.screen_surface = screen_surface
    while True:
        if GlobalState.game_status == GameStatus.MAIN_MENU:
            main_menu_phase()
        elif GlobalState.game_status == GameStatus.GAME_END:
            exit_phase()
        elif GlobalState.game_status == GameStatus.GAMEPLAY:
            gameplay_phase()
        pygame.display.update()
        pygame.time.Clock().tick(100)


if __name__ == "__main__":
    main()

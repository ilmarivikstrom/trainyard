"""Config."""

from typing import ClassVar


class Config:
    screen_width: int = 1600
    screen_height: int = 900
    padding_x: int = 64
    padding_y: int = 128
    FPS: int = 120
    cell_size: int = 64
    cells_x: int = 8
    cells_y: int = 8
    FPS_list: ClassVar[list[int]] = [5, 10, 20, 30, 60, 120, 240]
    draw_arcs: bool = False
    log_level: str = "INFO"
    play_music: bool = True

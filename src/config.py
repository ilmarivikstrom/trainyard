import math
from typing import List

class Config:
    screen_width: int = 1280
    screen_height: int = 720
    padding_x: int = 64
    padding_y: int = 64
    FPS: int = 100
    cell_size: int = 64
    cells_x: int = 8
    cells_y: int = 8
    FPS_list: List[int] = [5, 10, 20, 30, 60, 100, 200, 500, 1000]
    draw_arcs: bool = False
    log_level: str = "INFO"
    angular_vel: float = (math.pi / 2) / 48 # With 48 ticks per 90 degrees...
    play_music: bool = False

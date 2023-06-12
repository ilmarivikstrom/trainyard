from typing import List


class Config:
    screen_width: int = 1280
    screen_height: int = 720
    padding_x: int = 54
    padding_y: int = 118
    FPS: int = 150
    cell_size: int = 64
    cells_x: int = 8
    cells_y: int = 8
    FPS_list: List[int] = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
    draw_arcs: bool = False
    log_level: str = "INFO"
    play_music: bool = True

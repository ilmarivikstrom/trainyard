from configparser import ConfigParser


def read_config_file() -> ConfigParser:
    config = ConfigParser()
    config.read("config.ini")
    return config


class Config:
    screen_width = None
    screen_height = None
    padding_x = None
    padding_y = None
    FPS = None
    cell_size = None
    cells_x = None
    cells_y = None

    FPS_list = [5, 10, 20, 30, 60, 100, 200, 500, 1000]

    def setup(cfg: ConfigParser) -> None:
        Config.screen_width = int(cfg["SCREEN"]["WIDTH"])
        Config.screen_height = int(cfg["SCREEN"]["HEIGHT"])
        Config.padding_x = int(cfg["SCREEN"]["PADDING_X"])
        Config.padding_y = int(cfg["SCREEN"]["PADDING_Y"])
        Config.FPS = int(cfg["SCREEN"]["FPS"])
        Config.cell_size = int(cfg["SCREEN"]["CELL_SIZE"])
        Config.cells_x = int(cfg["SCREEN"]["CELLS_X"])
        Config.cells_y = int(cfg["SCREEN"]["CELLS_Y"])

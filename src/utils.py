import logging


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    fmt = "%(asctime)s %(funcName)20s(): %(message)s"
    logging.basicConfig(level=log_level, format=fmt)
    return logging.getLogger()


class SaveableAttributes:
    # Example:
    # TypeNumberColor:Orientation:PosI,PosJ
    # D1y:90:3,4
    # E:0:4,4
    # R:0:6,7
    # A4r:90:7,7
    def __init__(self, block_type=None, color=None, number=None, orientation=0, position=None):
        self.block_type = block_type
        self.color = str(color).rsplit(".", maxsplit=1)[-1][0].lower() # TrainColor.YELLOW --> 'y'
        self.number = number
        self.orientation = orientation
        self.position = position

    def serialize(self) -> str:
        if self.position:
            return f"{self.block_type}{self.number}{self.color}:{self.orientation}:{self.position[0]},{self.position[1]}"
        raise ValueError("Position must be initialized to some actual value.")

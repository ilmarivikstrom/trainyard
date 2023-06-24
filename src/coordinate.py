from typing import Tuple

class Coordinate:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: "Coordinate") -> bool: # TODO
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def copy(self) -> "Coordinate":
        return Coordinate(self.x, self.y)

    def as_tuple_float(self) -> Tuple[float, float]:
        return (float(self.x), float(self.y))

    def as_tuple_int(self) -> Tuple[int, int]:
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, source_tuple: Tuple[int, int]) -> "Coordinate":
        return cls(source_tuple[0], source_tuple[1])

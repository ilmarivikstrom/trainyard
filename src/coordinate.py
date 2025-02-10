"""Coordinate."""


class Coordinate:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        """Show string representation in (x, y) format."""
        return f"({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        """Check if two coordinates are equal."""
        return bool(
            isinstance(other, Coordinate) and self.x == other.x and self.y == other.y,
        )

    def copy(self) -> "Coordinate":
        return Coordinate(self.x, self.y)

    def as_tuple_float(self) -> tuple[float, float]:
        return (float(self.x), float(self.y))

    def as_tuple_int(self) -> tuple[int, int]:
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, source_tuple: tuple[int, int]) -> "Coordinate":
        x, y = source_tuple
        return cls(x, y)

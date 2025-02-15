"""Drawing cell."""

from src.coordinate import Coordinate
from src.graphics import Graphics
from src.levelitems.cell import Cell
from src.saveable import SaveableAttributes
from src.sound import Sound
from src.track import TrackType

MAXIMUM_TRACKS = 2


class DrawingCell(Cell):
    def __init__(self, coords: Coordinate) -> None:
        super().__init__(coords, Graphics.img_surfaces["bg_tile"], 0)
        self.saveable_attributes = SaveableAttributes(block_type="E")

    def unflippable_tracks(self, track_types: list[TrackType]) -> bool:
        return (
            (
                TrackType.BOTTOM_LEFT in track_types
                and TrackType.TOP_RIGHT in track_types
            )
            or (
                TrackType.TOP_LEFT in track_types
                and TrackType.BOTTOM_RIGHT in track_types
            )
            or (TrackType.VERT in track_types and TrackType.HORI in track_types)
        )

    def flip_tracks(self) -> None:
        if len(self.cell_tracks) < MAXIMUM_TRACKS:
            return
        track_types = [track.track_type for track in self.cell_tracks]
        if self.unflippable_tracks(track_types):
            return
        for track in self.cell_tracks:
            track.toggle_bright()
        self.cell_tracks.reverse()
        Sound.play_sound_on_any_channel(Sound.track_flip)

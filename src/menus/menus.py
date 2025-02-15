"""Menus."""

from __future__ import annotations

from src.config import Config
from src.font import Font
from src.menus.menubase import (
    GreenStyle,
    HorizontalMenu,
    IndicatorItem,
    RedStyle,
    VerticalMenu,
    WhiteStyle,
    YellowStyle,
)
from src.utils.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)


class BuildPurgeMenu(VerticalMenu):
    def __init__(self, topleft: tuple[int, int]) -> None:
        title = "ACTION (SHIFT)"
        menu_items: list[IndicatorItem] = [
            IndicatorItem(
                text="BUILD",
                padding_spaces=2,
                style=YellowStyle(),
                dest=topleft,
                font=Font.small,
            ),
            IndicatorItem(
                text="PURGE",
                padding_spaces=2,
                style=RedStyle(),
                dest=topleft,
                font=Font.small,
            ),
        ]
        super().__init__(topleft, title, menu_items)


class EditTestMenu(HorizontalMenu):
    def __init__(self, topleft: tuple[int, int]) -> None:
        title = "MODE (SPACE)"
        menu_items: list[IndicatorItem] = [
            IndicatorItem(
                text="EDIT",
                padding_spaces=3,
                style=WhiteStyle(),
                dest=topleft,
                font=Font.small,
            ),
            IndicatorItem(
                text="TEST",
                padding_spaces=3,
                style=WhiteStyle(),
                dest=topleft,
                font=Font.small,
            ),
        ]
        super().__init__(topleft, title, menu_items)


class RunningCrashedCompleteMenu(VerticalMenu):
    def __init__(self, topleft: tuple[int, int]) -> None:
        title = "LEVEL STATUS"
        menu_items: list[IndicatorItem] = [
            IndicatorItem(
                text="RUNNING",
                padding_spaces=3,
                style=YellowStyle(),
                dest=topleft,
                font=Font.small,
            ),
            IndicatorItem(
                text="CRASHED",
                padding_spaces=3,
                style=RedStyle(),
                dest=topleft,
                font=Font.small,
            ),
            IndicatorItem(
                text="COMPLETED",
                padding_spaces=3,
                style=GreenStyle(),
                dest=topleft,
                font=Font.small,
            ),
        ]
        super().__init__(topleft, title, menu_items)


class LevelMenu(VerticalMenu):
    def __init__(self, topleft: tuple[int, int], num_levels: int) -> None:
        title = "LEVEL (UP/DOWN)"
        menu_items: list[IndicatorItem] = [
            IndicatorItem(
                text=f"Level {i}",
                style=YellowStyle(),
                padding_spaces=2,
                dest=topleft,
                font=Font.small,
            )
            for i in range(num_levels)
        ]
        super().__init__(topleft, title, menu_items)


class InfoMenu(VerticalMenu):
    def __init__(self, topleft: tuple[int, int], tooltip_text: str, value: str) -> None:
        indicator_item = IndicatorItem(Font.small, value, 3, YellowStyle(), topleft)
        super().__init__(topleft, tooltip_text, [indicator_item])

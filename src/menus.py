from typing import List, Tuple

import pygame as pg

from src.color_constants import GRAY5, WHITE, TRAIN_GREEN, TRAIN_YELLOW, TRAIN_RED, WHITESMOKE
from src.config import Config
from src.font import Font
from src.indicator_item import IndicatorItem
from src.utils import setup_logging

logger = setup_logging(log_level=Config.log_level)

class Tooltip:
    def __init__(self, text: str, dest: Tuple[int, int]) -> None:
        self.surface: pg.Surface = Font.small.render(text, True, WHITE)
        self.dest: Tuple[int, int] = dest



class BaseMenu:
    def __init__(self, tooltip: Tooltip, indicator_items: List[IndicatorItem]) -> None:
        self.tooltip: Tooltip = tooltip
        self.indicator_items: List[IndicatorItem] = indicator_items

    def get_activated_items(self) -> List[int]:
        activated_items: List[int] = []
        for i, indicator_item in enumerate(self.indicator_items):
            if indicator_item.activated:
                activated_items.append(i)
        return activated_items


    def deactivate_all(self) -> None:
        for indicator_item in self.indicator_items:
            indicator_item._deactivate()


    def activate_item(self, item_to_activate: int) -> None:
        if item_to_activate > len(self.indicator_items) - 1 or item_to_activate < 0:
            logger.warning(f"Trying to activate menu item {item_to_activate} when there are only {len(self.indicator_items)} items available.")
            return
        for i, indicator_item in enumerate(self.indicator_items):
            if i == item_to_activate:
                indicator_item._activate()
            else:
                indicator_item._deactivate()


    def activate_next_item(self) -> None:
        activated_item = None
        for i, indicator_item in enumerate(self.indicator_items):
            if indicator_item.activated:
                activated_item = i
                break
        final_item = len(self.indicator_items) - 1
        if activated_item is None or activated_item == final_item:
            next_item = final_item
        else:
            next_item = activated_item + 1
        self.activate_item(next_item)


    def activate_previous_item(self) -> None:
        activated_item = None
        for i, indicator_item in enumerate(self.indicator_items):
            if indicator_item.activated:
                activated_item = i
                break
        start_item = 0
        if activated_item is None or activated_item == start_item:
            next_item = start_item
        else:
            next_item = activated_item - 1
        self.activate_item(next_item)


    def draw(self, screen_surface: pg.Surface) -> None:
        screen_surface.blit(self.tooltip.surface, self.tooltip.dest)
        for indicator_item in self.indicator_items:
            screen_surface.blit(indicator_item.rendered, indicator_item.dest)



class BuildPurgeMenu(BaseMenu):
    def __init__(self, topleft: Tuple[int, int]) -> None:
        self.topleft: Tuple[int, int] = topleft
        self.row_height = 20

        self.tooltip = Tooltip("L-SHIFT", (self.topleft[0] + 32, self.topleft[1]))

        self.first = IndicatorItem(
            font=Font.normal,
            text="BUILD",
            padding_spaces=2,
            activated_text_color=GRAY5,
            activated_bg_color=TRAIN_YELLOW,
            dest=(self.topleft[0], self.topleft[1] + 1 * self.row_height)
        )
        self.second = IndicatorItem(
            font=Font.normal,
            text="PURGE",
            padding_spaces=2,
            activated_text_color=GRAY5,
            activated_bg_color=TRAIN_RED,
            dest=(self.topleft[0], self.topleft[1] + 2 * self.row_height)
        )
        super().__init__(self.tooltip, [self.first, self.second])



class EditTestMenu(BaseMenu):
    def __init__(self, topleft: Tuple[int, int]) -> None:
        self.topleft: Tuple[int, int] = topleft
        self.row_height = 20

        self.tooltip = Tooltip("SPACEBAR", (self.topleft[0] + 96, self.topleft[1]))

        self.first = IndicatorItem(
            font=Font.normal,
            text="EDIT",
            padding_spaces=3,
            activated_text_color=GRAY5,
            activated_bg_color=WHITESMOKE,
            dest=(self.topleft[0], self.topleft[1] + 1 * self.row_height)
        )
        self.second = IndicatorItem(
            font=Font.normal,
            text="TEST",
            padding_spaces=3,
            activated_text_color=GRAY5,
            activated_bg_color=WHITESMOKE,
            dest=(self.topleft[0] + 128, self.topleft[1] + 1 * self.row_height)
        )
        super().__init__(self.tooltip, [self.first, self.second])




class RunningCrashedCompleteMenu(BaseMenu):
    def __init__(self, topleft: Tuple[int, int]) -> None:
        self.topleft: Tuple[int, int] = topleft
        self.row_height = 20

        self.tooltip = Tooltip("LEVEL STATUS", (self.topleft[0] + 36, self.topleft[1]))

        self.first = IndicatorItem(
            font=Font.normal,
            text="RUNNING",
            padding_spaces=3,
            activated_text_color=GRAY5,
            activated_bg_color=TRAIN_YELLOW,
            dest=(self.topleft[0], self.topleft[1] + 1 * self.row_height)
        )
        self.second = IndicatorItem(
            font=Font.normal,
            text="CRASHED",
            padding_spaces=3,
            activated_text_color=GRAY5,
            activated_bg_color=TRAIN_RED,
            dest=(self.topleft[0], self.topleft[1] + 2 * self.row_height)
        )
        self.third = IndicatorItem(
            font=Font.normal,
            text="COMPLETE",
            padding_spaces=3,
            activated_text_color=GRAY5,
            activated_bg_color=TRAIN_GREEN,
            dest=(self.topleft[0], self.topleft[1] + 3 * self.row_height)
        )
        super().__init__(self.tooltip, [self.first, self.second, self.third])



class LevelMenu(BaseMenu):
    def __init__(self, topleft: Tuple[int, int]) -> None:
        self.topleft: Tuple[int, int] = topleft
        self.row_height = 20

        self.tooltip = Tooltip("LEVEL SELECT", (self.topleft[0] + 36, self.topleft[1]))

        self.first = IndicatorItem(
            font=Font.normal,
            text="LEVEL 0",
            padding_spaces=3,
            activated_text_color=GRAY5,
            activated_bg_color=TRAIN_YELLOW,
            dest=(self.topleft[0], self.topleft[1] + 1 * self.row_height)
        )
        self.second = IndicatorItem(
            font=Font.normal,
            text="LEVEL 1",
            padding_spaces=3,
            activated_text_color=GRAY5,
            activated_bg_color=TRAIN_YELLOW,
            dest=(self.topleft[0], self.topleft[1] + 2 * self.row_height)
        )
        self.third = IndicatorItem(
            font=Font.normal,
            text="LEVEL 2",
            padding_spaces=3,
            activated_text_color=GRAY5,
            activated_bg_color=TRAIN_YELLOW,
            dest=(self.topleft[0], self.topleft[1] + 3 * self.row_height)
        )
        super().__init__(self.tooltip, [self.first, self.second, self.third])

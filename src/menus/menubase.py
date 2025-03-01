"""Menu base."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.color_constants import (
    GRAY5,
    GRAY50,
    TY_GREEN,
    TY_RED,
    TY_TELLOW,
    WHITE,
    WHITESMOKE,
)
from src.config import Config
from src.font import Font
from src.utils.utils import setup_logging

if TYPE_CHECKING:
    import pygame as pg

    from src.coordinate import Coordinate

logger = setup_logging(log_level=Config.LOG_LEVEL)


class IndicatorStyle:
    def __init__(
        self,
        fg_active_color: tuple[int, int, int] = GRAY5,
        bg_active_color: tuple[int, int, int] = TY_TELLOW,
        fg_deactive_color: tuple[int, int, int] = GRAY50,
        bg_deactive_color: tuple[int, int, int] = GRAY5,
    ) -> None:
        self.fg_active_color = fg_active_color
        self.bg_active_color = bg_active_color
        self.fg_deactive_color = fg_deactive_color
        self.bg_deactive_color = bg_deactive_color

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__


class YellowStyle(IndicatorStyle):
    def __init__(self) -> None:
        super().__init__(bg_active_color=TY_TELLOW)


class RedStyle(IndicatorStyle):
    def __init__(self) -> None:
        super().__init__(bg_active_color=TY_RED)


class GreenStyle(IndicatorStyle):
    def __init__(self) -> None:
        super().__init__(bg_active_color=TY_GREEN)


class WhiteStyle(IndicatorStyle):
    def __init__(self) -> None:
        super().__init__(bg_active_color=WHITESMOKE)


class IndicatorItem:
    def __init__(
        self,
        font: pg.Font,
        text: str,
        padding_spaces: int,
        style: IndicatorStyle,
        dest: tuple[int, int],
    ) -> None:
        self.font: pg.Font = font
        self.text: str = text
        self.padding_spaces: int = padding_spaces
        self.style = style
        self.dest: tuple[int, int] = dest

        self.activated: bool = False
        self.render()

    def render(self) -> None:
        if self.activated:
            self.renderable = self.font.render(
                f"{self.text:^{len(self.text) + 2 * self.padding_spaces}}",
                antialias=True,
                color=self.style.fg_active_color,
                bgcolor=self.style.bg_active_color,
            )
        else:
            self.renderable = self.font.render(
                f"{self.text:^{len(self.text) + 2 * self.padding_spaces}}",
                antialias=True,
                color=self.style.fg_deactive_color,
                bgcolor=self.style.bg_deactive_color,
            )

    def activate(self) -> None:
        self.activated = True
        self.render()

    def deactivate(self) -> None:
        self.activated = False
        self.render()


class Tooltip:
    def __init__(self, text: str, dest: tuple[int, int]) -> None:
        self.surface: pg.Surface = Font.normal.render(text, antialias=True, color=WHITE)
        self.dest: tuple[int, int] = dest


class BaseMenu:
    def __init__(
        self,
        topleft: tuple[int, int],
        tooltip: Tooltip,
        indicator_items: list[IndicatorItem],
    ) -> None:
        self.topleft = topleft
        self.tooltip: Tooltip = tooltip
        self._indicator_items: list[IndicatorItem] = indicator_items

    def get_activated_items(self) -> list[int]:
        activated_items: list[int] = []
        for i, indicator_item in enumerate(self._indicator_items):
            if indicator_item.activated:
                activated_items.append(i)
        return activated_items

    def set_text(self, text: str, item_index: int) -> None:
        if item_index > len(self._indicator_items) - 1:
            msg = f"Tried to set text for indicator item in index {item_index}"
            " when the maximum index is {len(self._indicator_items) - 1}"
            raise ValueError(
                msg,
            )
        self._indicator_items[item_index].text = text
        self._indicator_items[item_index].render()

    def deactivate_all(self) -> None:
        for indicator_item in self._indicator_items:
            indicator_item.deactivate()

    def activate_item(self, item_to_activate: int) -> None:
        if item_to_activate > len(self._indicator_items) - 1 or item_to_activate < 0:
            logger.warning(
                f"Trying to activate menu item {item_to_activate} when"
                " there are only {len(self._indicator_items)} items available.",
            )
            return
        for i, indicator_item in enumerate(self._indicator_items):
            if i == item_to_activate:
                indicator_item.activate()
            else:
                indicator_item.deactivate()

    def activate_next_item(self) -> None:
        activated_item = None
        for i, indicator_item in enumerate(self._indicator_items):
            if indicator_item.activated:
                activated_item = i
                break
        final_item = len(self._indicator_items) - 1
        if activated_item is None or activated_item == final_item:
            next_item = final_item
        else:
            next_item = activated_item + 1
        self.activate_item(next_item)

    def activate_previous_item(self) -> None:
        activated_item = None
        for i, indicator_item in enumerate(self._indicator_items):
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
        for indicator_item in self._indicator_items:
            screen_surface.blit(indicator_item.renderable, indicator_item.dest)

    def mouse_on(self, mouse_pos: Coordinate) -> bool:
        # TODO: Get absolute position of tooltip and indicat items NOT on the fly.
        if (
            self.tooltip.surface.get_rect()
            .move(self.topleft)
            .collidepoint(mouse_pos.as_tuple_float())
        ):
            logger.info("Collides with tooltip.")
            return True
        for i, indicator_item in enumerate(self._indicator_items):
            if (
                indicator_item.renderable.get_rect()
                .move(indicator_item.dest)
                .collidepoint(mouse_pos.as_tuple_float())
            ):
                logger.info(f"Collides with indicator item: {i}")
                return True
        return False


class VerticalMenu(BaseMenu):
    def __init__(
        self,
        topleft: tuple[int, int],
        title: str,
        menu_items: list[IndicatorItem],
    ) -> None:
        self.topleft: tuple[int, int] = topleft
        self.title: str = title
        self.menu_items = menu_items
        self.row_height: int = 20

        self.tooltip = Tooltip(title, (self.topleft[0], self.topleft[1]))

        self.indicator_items: list[IndicatorItem] = []

        # TODO: Why on earth am I creating a list[IndicatorItem] again??
        for i, menu_item in enumerate(menu_items):
            self.indicator_items.append(
                IndicatorItem(
                    font=Font.normal,
                    text=menu_item.text,
                    padding_spaces=3,
                    style=menu_item.style,
                    dest=(self.topleft[0], self.topleft[1] + (i + 1) * self.row_height),
                ),
            )

        super().__init__(self.topleft, self.tooltip, self.indicator_items)


class HorizontalMenu(BaseMenu):
    def __init__(
        self,
        topleft: tuple[int, int],
        title: str,
        menu_items: list[IndicatorItem],
    ) -> None:
        self.topleft: tuple[int, int] = topleft
        self.title: str = title
        self.menu_items = menu_items
        self.row_height: int = 20
        self.row_width: int = 128

        self.tooltip = Tooltip(title, (self.topleft[0], self.topleft[1]))

        self.indicator_items: list[IndicatorItem] = []

        # TODO: Why on earth am I creating a list[IndicatorItem] again??
        for i, menu_item in enumerate(menu_items):
            self.indicator_items.append(
                IndicatorItem(
                    font=Font.normal,
                    text=menu_item.text,
                    padding_spaces=3,
                    style=menu_item.style,
                    dest=(
                        self.topleft[0] + i * self.row_width,
                        self.topleft[1] + 1 * self.row_height,
                    ),
                ),
            )

        super().__init__(self.topleft, self.tooltip, self.indicator_items)

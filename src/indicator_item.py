from typing import Tuple

import pygame as pg

class IndicatorItem:
    def __init__(self, font: pg.Font, text: str, padding_spaces: int, activated_text_color: Tuple[int, int, int], activated_bg_color: Tuple[int, int, int, int], dest: Tuple[int, int]) -> None:
        self.font: pg.Font = font
        self.text: str = text
        self.padding_spaces: int = padding_spaces
        self.activated_text_color: Tuple[int, int, int] = activated_text_color
        self.activated_bg_color: Tuple[int, int, int] = activated_bg_color
        self.dest: Tuple[int, int] = dest
        self.deactivated_text_color: Tuple[int, int, int] = (127, 127, 127)
        self.deactivated_bg_color: Tuple[int, int, int] = (13, 13, 13)

        self.activated: bool = False
        self.render()


    def render(self):
        if self.activated:
            self.rendered = self.font.render(f"{self.text:^{len(self.text) + 2 * self.padding_spaces}}", True, self.activated_text_color, self.activated_bg_color)
        else:
            self.rendered = self.font.render(f"{self.text:^{len(self.text) + 2 * self.padding_spaces}}", True, self.deactivated_text_color, self.deactivated_bg_color)


    def _activate(self):
        self.activated = True
        self.render()


    def _deactivate(self):
        self.activated = False
        self.render()

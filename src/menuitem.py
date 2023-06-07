from typing import Tuple

import pygame as pg

class MenuItem:
    def __init__(self, font: pg.Font, text: str, padding: int, activated_text_color: Tuple[int, int, int], activated_bg_color: Tuple[int, int, int, int], dest: Tuple[int, int]) -> None:
        self.font = font
        self.text = text
        self.padding = padding
        self.activated_text_color = activated_text_color
        self.activated_bg_color = activated_bg_color
        self.deactivated_text_color = (127, 127, 127)
        self.deactivated_bg_color = (13, 13, 13)
        self.dest = dest

        self.activated = False

        self.render()


    def render(self):
        if self.activated:
            self.rendered = self.font.render(f"{self.text:^{len(self.text) + 2 * self.padding}}", True, self.activated_text_color, self.activated_bg_color)
        else:
            self.rendered = self.font.render(f"{self.text:^{len(self.text) + 2 * self.padding}}", True, self.deactivated_text_color, self.deactivated_bg_color)


    def activate(self):
        self.activated = True
        self.render()


    def deactivate(self):
        self.activated = False
        self.render()

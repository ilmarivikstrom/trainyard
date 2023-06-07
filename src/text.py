import pygame as pg

class Text:
    @staticmethod
    def get_font_with_size(size: int) -> pg.Font:
        font = pg.font.Font(filename="assets/fonts/Walter-Heavy.otf", size=size)
        return font

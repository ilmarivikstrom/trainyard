import pygame as pg


class Sound:
    pg.mixer.pre_init(44100, -16, 1, 512)
    pg.mixer.init()
    pg.init()

    crash = pg.mixer.Sound("res/crash.mp3")
    crash.set_volume(0.2)

    merge = pg.mixer.Sound("res/merge.wav")
    merge.set_volume(0.2)

    pop = pg.mixer.Sound("res/pop.mp3")
    pop.set_volume(0.2)

    track_flip = pg.mixer.Sound("res/click.wav")
    track_flip.set_volume(0.2)

    success = pg.mixer.Sound("res/achievement.wav")
    success.set_volume(0.5)

    @staticmethod
    def play_sound_on_channel(sound, channel):
        pg.mixer.Channel(channel).play(sound)

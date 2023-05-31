import pygame as pg


class Sound:
    pg.mixer.pre_init(44100, -16, 1, 512)
    pg.mixer.init()
    pg.init()

    master_volume = 1.0

    crash = pg.mixer.Sound("res/crash.mp3")
    crash.set_volume(0.4 * master_volume)

    merge = pg.mixer.Sound("res/merge.wav")
    merge.set_volume(0.4 * master_volume)

    pop = pg.mixer.Sound("res/pop.mp3")
    pop.set_volume(0.4 * master_volume)

    track_flip = pg.mixer.Sound("res/click.wav")
    track_flip.set_volume(0.4 * master_volume)

    success = pg.mixer.Sound("res/achievement.wav")
    success.set_volume(1.0 * master_volume)

    @staticmethod
    def play_sound_on_channel(sound: pg.mixer.Sound, channel: int) -> None:
        pg.mixer.Channel(channel).play(sound)

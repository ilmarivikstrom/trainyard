import pygame as pg


class Sound:
    pg.mixer.pre_init(frequency=44100, size=-16, channels=3, buffer=512)
    pg.mixer.init()
    pg.init()

    master_volume = 1.0

    crash = pg.mixer.Sound("assets/sounds/crash.mp3")
    crash.set_volume(0.4 * master_volume)

    merge = pg.mixer.Sound("assets/sounds/merge.wav")
    merge.set_volume(0.4 * master_volume)

    pop = pg.mixer.Sound("assets/sounds/pop.mp3")
    pop.set_volume(0.4 * master_volume)

    track_flip = pg.mixer.Sound("assets/sounds/click.wav")
    track_flip.set_volume(0.1 * master_volume)

    success = pg.mixer.Sound("assets/sounds/achievement.wav")
    success.set_volume(1.0 * master_volume)

    @staticmethod
    def play_sound_on_channel(sound: pg.mixer.Sound, channel: int) -> None:
        pg.mixer.Channel(channel).play(sound)

    @staticmethod
    def play_music() -> None:
        pg.mixer.music.load("assets/sounds/cyberpunk_synthwave2.mp3")
        pg.mixer.music.set_volume(0.03)
        pg.mixer.music.play(-1)

    @staticmethod
    def stop_music() -> None:
        pg.mixer.music.stop()
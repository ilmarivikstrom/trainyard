import pygame as pg


class Sound:
    pg.mixer.pre_init(frequency=44100, size=-16, channels=3, buffer=512)
    pg.mixer.init()
    pg.init()  # pylint: disable=no-member; # TODO: Add game_loop.py and clean main.py as the entry point, move pg.init() there.

    master_volume = 1.0

    music_playing = False

    crash = pg.mixer.Sound("assets/sounds/Modern9.ogg")
    crash.set_volume(0.1 * master_volume)

    merge = pg.mixer.Sound("assets/sounds/merge.wav")
    merge.set_volume(0.03 * master_volume)

    pop = pg.mixer.Sound("assets/sounds/pop.ogg")
    pop.set_volume(0.1 * master_volume)

    track_flip = pg.mixer.Sound("assets/sounds/Minimalist13_short.ogg")
    track_flip.set_volume(0.1 * master_volume)

    track_place = pg.mixer.Sound("assets/sounds/Minimalist13_short.ogg")
    track_place.set_volume(0.1 * master_volume)

    success = pg.mixer.Sound("assets/sounds/achievement.wav")
    success.set_volume(0.1 * master_volume)

    spark = pg.mixer.Sound("assets/sounds/pop1.ogg")
    spark.set_volume(0.2 * master_volume)


    @staticmethod
    def play_sound_on_channel(sound: pg.mixer.Sound, channel: int) -> None:
        pg.mixer.Channel(channel).play(sound)


    @staticmethod
    def play_sound_on_any_channel(sound: pg.mixer.Sound) -> None:
        pg.mixer.find_channel(force=True).play(sound)


    @staticmethod
    def init_music() -> None:
        pg.mixer.music.load("assets/sounds/Loop.ogg")
        pg.mixer.music.set_volume(0.02 * Sound.master_volume)


    @staticmethod
    def play_music() -> None:
        pg.mixer.music.play(-1)
        Sound.music_playing = True


    @staticmethod
    def stop_music() -> None:
        pg.mixer.music.stop()
        Sound.music_playing = False


    @staticmethod
    def fadeout_music(ms: int) -> None:
        pg.mixer.music.fadeout(ms)
        Sound.music_playing = False


    @staticmethod
    def toggle_music(ms: int) -> None:
        if Sound.music_playing:
            Sound.fadeout_music(ms)
        else:
            Sound.play_music()

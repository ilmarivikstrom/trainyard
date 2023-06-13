from typing import Dict

import pygame as pg


class Sound:
    pg.mixer.pre_init(frequency=44100, size=-16, channels=3, buffer=512)
    pg.mixer.init()
    pg.init()  # pylint: disable=no-member; # TODO: Add game_loop.py and clean main.py as the entry point, move pg.init() there.

    base_path = "assets/sounds/"
    song_paths: Dict[str, str] = {
        "Song 1": base_path + "Loop.ogg",
        "Song 2": base_path + "Ludum-Dare-28-Track-7.ogg",
        "Song 3": base_path + "Ludum-Dare-30-Track-6.ogg",
        "Song 4": base_path + "Ludum-Dare-32-Track-3.ogg",
        "Song 5": base_path + "Ludum-Dare-32-Track-5.ogg",
        "Song 6": base_path + "Ludum-Dare-38-Track-2.ogg",
        "Song 7": base_path + "Ludum-Dare-38-Track-7.ogg",
        "Song 8": base_path + "Ludum-Dare-38-Track-8.ogg",
        "Song 9": base_path + "Ludum-Dare-38-Track-10.ogg",
    }

    master_volume = 1.0

    music_playing = False

    crash = pg.mixer.Sound("assets/sounds/Modern9.ogg")
    crash.set_volume(0.1 * master_volume)

    merge = pg.mixer.Sound("assets/sounds/merge.ogg")
    merge.set_volume(0.03 * master_volume)

    pop = pg.mixer.Sound("assets/sounds/pop.ogg")
    pop.set_volume(0.1 * master_volume)

    track_flip = pg.mixer.Sound("assets/sounds/Minimalist13_short.ogg")
    track_flip.set_volume(0.1 * master_volume)

    track_place = pg.mixer.Sound("assets/sounds/Minimalist13_short.ogg")
    track_place.set_volume(0.1 * master_volume)

    success = pg.mixer.Sound("assets/sounds/achievement.ogg")
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
    def init_music(song_name: str) -> None:
        pg.mixer.music.load(Sound.song_paths[song_name])
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

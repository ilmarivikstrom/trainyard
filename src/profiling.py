"""Profiling."""

import cProfile
import os
import pstats
import time

import psutil


class Profiler:
    def __init__(self) -> None:
        self.is_running = False
        self.profile = cProfile.Profile(builtins=False)
        self.start_time = 0
        self.end_time = 0
        self.ticks = 0
        self._pid = os.getpid()
        self.process = psutil.Process(self._pid)

    def discontinue_profiling(self) -> None:
        if not self.is_running:
            return
        print("INFO\tstopped profiling!")
        self.end_time = time.time()
        print(f"Total profiling time: {(self.end_time - self.start_time):.2f} seconds")
        self.profile.disable()
        sort_by = "tottime"
        stats = pstats.Stats(self.profile)
        stats.strip_dirs()
        stats.sort_stats(sort_by)

        self.print_psutils()

        stats.print_stats(35)
        self.is_running = False

    def continue_profiling(self) -> None:
        if self.is_running:
            self.ticks += 1
            return
        print("INFO\tstarted profiling...")
        self.ticks = 0
        self.start_time = time.time()
        self.profile.clear()  # type: ignore
        self.profile.enable()
        self.is_running = True

    def print_psutils(self) -> None:
        print(
            f"Process:\n"
            f"=========================\n"
            f"PID: {self._pid}\n"
            f"CPU times: {self.process.cpu_times()}\n"
            f"CPU percentage: {self.process.cpu_percent(interval=None)}\n"
            f"Memory info: {self.process.memory_full_info()} \n"
            f"Memory percentage: {self.process.memory_percent()}\n\n\n"
            f"Profiler info:\n"
            f"=========================\n",
        )

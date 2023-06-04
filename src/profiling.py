import cProfile
import pstats

class Profiler:
    def __init__(self):
        self.is_running = False
        self.profile = cProfile.Profile(builtins=False)


    def discontinue_profiling(self):
        if not self.is_running:
            return
        print("INFO\tstopped profiling!")
        self.profile.disable()
        sort_by = "tottime"
        stats = pstats.Stats(self.profile)
        stats.strip_dirs()
        stats.sort_stats(sort_by)
        stats.print_stats(35)
        self.is_running = False


    def continue_profiling(self):
        if self.is_running:
            return
        print("INFO\tstarted profiling...")
        self.profile.clear() # type: ignore
        self.profile.enable()
        self.is_running = True

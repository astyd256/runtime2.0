
from threading import local, RLock
from cProfile import Profile
from pstats import Stats

import settings
from logs import server_log


class ProfilerLocal(local):

    counter = 0
    profile = None


class Profiler(object):

    def __init__(self):
        self._lock = RLock()
        self._stats = None
        self._local = ProfilerLocal()

    def __enter__(self):
        if not settings.PROFILING:
            return self

        if not self._local.counter:
            self._local.profile = Profile()
            self._local.profile.enable()
        self._local.counter += 1
        return self

    def __exit__(self, extype, exvalue, extraceback):
        if not settings.PROFILING:
            return

        self._local.counter -= 1
        if not self._local.counter:
            self.aggregate(self._local.profile)
            self._local.profile = None

    def aggregate(self, profile_or_stats):
        with self._lock:
            if self._stats is None:
                self._stats = Stats(profile_or_stats)
            else:
                self._stats.add(profile_or_stats)

    def save(self, location=None):
        if not settings.PROFILING:
            return

        if location is None:
            location = settings.PROFILE_LOCATION

        if self._stats:
            self._stats.dump_stats(location)
            server_log.write("Save profiling statistics to \"%s\"" % location)


profiler = Profiler()

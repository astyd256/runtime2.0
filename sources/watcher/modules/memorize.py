
import managers


def memorize(options):
    managers.server.watcher.snapshot.start()
    yield "<reply/>"

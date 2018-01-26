
from logs import log
from utils import verificators
from utils.profiling import profiler
from ..exceptions import OptionError


def profiling(options):
    status = options.get("status")
    if status is not None:
        try:
            status = verificators.enable_or_disable(status)
        except ValueError:
            raise OptionError("Incorrect status")

        if profiler.status != status:
            log.write("%s profiling" % ("Enable" if status else "Disable"))
            profiler.status = status
            if not status:
                profiler.clear()

    status = "enabled" if profiler.status else "disabled"
    yield "<reply><profiling><status>%s</status></profiling></reply>" % status

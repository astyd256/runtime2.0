
import re
from logs import log
from utils.profiling import profiler
from ..exceptions import OptionError


STATUS_REGEX = re.compile("enable$|disable$", re.MULTILINE)


def profiling(options):
    status = options.get("status")
    if status is not None:
        if not STATUS_REGEX.match(status):
            raise OptionError("Incorrect status")
        status = status == "enable"
        if profiler.status != status:
            log.write("%s profiling" % ("Enable" if status else "Disable"))
            profiler.status = status
            if not status:
                profiler.clear()

    status = "enabled" if profiler.status else "disabled"
    yield "<reply><profiling><status>%s</status></profiling></reply>" % status

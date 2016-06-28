
import managers
from .auxiliary import section, show


def run():
    """
    show installed applications and types
    """
    with section("types"):
        types = sorted(managers.memory.types.itervalues(), key=lambda item: item.name)
        for vdomtype in types:
            show(vdomtype.id + ":%s" % vdomtype.name)

    with section("applications"):
        applications = sorted(managers.memory.applications.itervalues(), key=lambda item: item.name)
        for application in applications:
            show(application.id + ":%s" % application.name.lower())

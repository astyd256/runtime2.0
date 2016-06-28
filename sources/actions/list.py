
import managers
from .auxiliary import section, show


def run():
    """
    show installed applications and types
    """
    types = sorted(managers.memory.types.itervalues(), key=lambda item: item.name)
    with section("types"):
        for type in types:
            show(type.id + (":%s" % type.name if type else ""))

    applications = sorted(managers.memory.applications.itervalues(), key=lambda item: item.name)
    with section("applications"):
        for application in applications:
                show(application.id + ":%s" % application.name.lower())

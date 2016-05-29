
import managers
from logs import console
from .auxiliary import section, show


def run():
    """
    show installed applications and types
    """

    types = sorted(managers.memory.types.itervalues(), key=lambda item: item.name)
    with section("types"):
        for type in types:
            try:
                show(type.id + (":%s" % type.name if type else ""))
            except Exception as error:
                console.error("unable to list type: %s" % error)

    applications = sorted(managers.memory.applications.itervalues(), key=lambda item: item.name)
    with section("applications"):
        for application in applications:
            try:
                show(application.id + ":%s" % application.name.lower())
            except Exception as error:
                console.error("unable to list application: %s" % error)

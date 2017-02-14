
import managers
from .auxiliary import section, show


def run():
    """
    update memory index
    """
    managers.memory.types.save()
    with section("write memory index", lazy=False):
        show("done")

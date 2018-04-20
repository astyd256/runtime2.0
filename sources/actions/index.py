
import managers
from .auxiliary import show


def run():
    """
    update memory index
    """
    managers.memory.types.save()
    show("write memory index")

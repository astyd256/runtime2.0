
from uuid import uuid4
from .auxiliary import show


def run():
    """
    generate unique identifier
    """
    show(uuid4())

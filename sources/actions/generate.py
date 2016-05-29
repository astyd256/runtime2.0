
from uuid import uuid4
from logs import console


def run():
    """
    generate unique identifier
    """
    console.write(str(uuid4()))


from ..auxiliary import subparser
from .elements import elements


@subparser
def anyway(self, selector, iterator):
    """
    Handle all inner elements with handler
    """

    def anyway_selector(name):
        return selector

    elements(self, anyway_selector, iterator)

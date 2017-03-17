
import settings
from .auxiliary.constants import TYPES, APPLICATIONS
from .auxiliary import section, show, select


ENTITIES = TYPES, APPLICATIONS


def run(identifier="all"):
    """
    cleanup bytecode cache application or type
    :param uuid_or_name identifier: application or type uuid or name
    """
    if not settings.STORE_BYTECODE:
        show("storing is disabled")
        return

    for entity, subject in select(identifier, "cleanup", ENTITIES):
        with section("cleanup %s" % subject, lazy=False):
            try:
                subject.cleanup()
            except Exception as error:
                show("unable to recompile %s: %s" % (entity, error))
                raise

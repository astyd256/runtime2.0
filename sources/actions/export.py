
import os.path
from .auxiliary.constants import REPOSITORY, TYPES, APPLICATIONS
from .auxiliary import section, show, satisfy, select, autocomplete, locate_repository


ENTITIES = TYPES, APPLICATIONS


def run(identifier, location=None, excess=False, yes=False):
    """
    export application or type
    :param uuid_or_name identifier: uuid or name of application or type or "types"
    :param location: output file or directory (repository by default)
    :param switch excess: export excess information (like attributes with default values)
    :param switch yes: assume positive answer to confirmation request
    """
    if location in REPOSITORY:
        location = None

    if satisfy(identifier, ENTITIES) and location and not os.path.isdir(location):
        show("not a directory: %s" % location)
        return

    for entity, subject in select(identifier, "export", ENTITIES, confirm=not yes):
        entity_location = location or locate_repository(entity)
        with section("export %s to %s" % (subject, entity_location), lazy=False):
            try:
                subject.export(autocomplete(subject, entity_location), excess=excess)
            except Exception as error:
                show("unable to export %s: %s" % (entity, error))
                raise

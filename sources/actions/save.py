
from .auxiliary import section, show
from .detecting import search


def run(identifier):
    """
    re-save application or type
    :param uuid_or_name identifier: application or type uuid or name
    """
    entity, subject = search(identifier)
    if subject:
        with section("re-save %s %s: %s" % (entity, subject.id, subject.name), instant=True):
            try:
                subject.save()
            except Exception as error:
                show("unable to save %s: %s" % (entity, error))
                raise

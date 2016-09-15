
from .auxiliary import section, show, search


def run(identifier):
    """
    re-save application or type
    :param uuid_or_name identifier: application or type uuid or name
    """
    entity, subject = search(identifier)
    if subject:
        with section("re-save %s %s: %s" % (entity, subject.id, subject.name), lazy=False):
            try:
                subject.save()
            except Exception as error:
                show("unable to save %s: %s" % (entity, error))

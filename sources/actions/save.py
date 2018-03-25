
from .auxiliary import section, warn, search


def run(identifier):
    """
    re-save application or type
    :arg uuid_or_name identifier: application or type uuid or name
    """
    entity, subject = search(identifier)
    if subject:
        with section("re-save %s %s: %s" % (entity, subject.id, subject.name), lazy=False):
            try:
                subject.save()
            except Exception as error:
                warn("unable to save %s: %s" % (entity, error))
                raise

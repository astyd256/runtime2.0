
from logs import console
from .detecting import search


def run(identifier):
    """
    re-save application or type
    :param uuid_or_name identifier: application or type uuid or name
    """
    entity, subject = search(identifier)
    if subject:
        console.write("re-save %s %s: %s" % (entity, subject.id, subject.name))
        try:
            subject.save()
        except Exception as error:
            console.error("unable to save %s: %s" % (entity, error))
            raise

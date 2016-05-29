
import managers
from logs import console


TYPE = "type"
APPLICATION = "application"


def run(uuid_or_name):
    """
    re-save application or type
    :param uuid_or_name uuid_or_name: application or type uuid or name
    """

    subject = managers.memory.types.search(uuid_or_name)
    if subject:
        console.write("re-save type %s: %s" % (subject.id, subject.name))
        entity = TYPE
    else:
        subject = managers.memory.applications.search(uuid_or_name)
        if subject:
            console.write("re-save application %s: %s" % (subject.id, subject.name.lower()))
            entity = APPLICATION
        else:
            console.error("unable to find application or type with such uuid or name")
            return

    try:
        subject.save()
    except Exception as error:
        console.error("unable to save %s: %s" % (entity, error))
        raise


import managers
from logs import console


TYPE = "type"
APPLICATION = "application"


def run(uuid_or_name):
    """
    uninstall application or type
    :param uuid_or_name uuid_or_name: application or type uuid or name
    """

    subject = managers.memory.types.search(uuid_or_name)
    if subject:
        console.write("uninstall type %s: %s" % (subject.id, subject.name))
        entity = TYPE
    else:
        subject = managers.memory.applications.search(uuid_or_name)
        if subject:
            console.write("uninstall application %s: %s" % (subject.id, subject.name.lower()))
            entity = APPLICATION
        else:
            console.error("unable to find application or type with such uuid")
            return

    try:
        subject.uninstall()
    except Exception as error:
        console.error("unable to uninstall %s: %s" % (entity, error))
        raise

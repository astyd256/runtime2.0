
import os.path
import managers
from logs import console


TYPE = "type"
APPLICATION = "application"


def run(identifier, location):
    """
    export application or type
    :param identifier uuid_or_name: uuid or name of application or type or "types"
    :param location: output file or directory
    """

    def export(entity, subject, location):
        console.write("export %s %s: %s to %s" % (entity, subject.id, subject.name, location))
        try:
            subject.export(location)
        except Exception as error:
            console.error("unable to export %s: %s" % (entity, error))
            raise

    if identifier == "types":
        if not os.path.isdir(location):
            console.error("location must be directory for exporting types")
            return

        for subject in managers.memory.types.itervalues():
            export(TYPE, subject, os.path.join(location, subject.name + ".xml"))
    else:
        subject = managers.memory.types.search(identifier)
        if subject:
            entity = TYPE
        else:
            subject = managers.memory.applications.search(identifier)
            if subject:
                entity = APPLICATION
            else:
                console.error("unable to find application or type with such uuid or name")
                return

        if os.path.isdir(location):
            location = os.path.join(location, subject.name + ".xml")
        elif not location.endswith(".xml"):
            location += ".xml"

        export(entity, subject, location)

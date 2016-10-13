
from contextlib import closing
import managers
import file_access
from logs import console
from utils.parsing import native, Parser
from .constants import TYPE, APPLICATION


def search(identifier):
    subject = managers.memory.types.search(identifier)
    if subject:
        return TYPE, subject
    else:
        subject = managers.memory.applications.search(identifier)
        if subject:
            return APPLICATION, subject
        else:
            console.error("unable to find application or type with such uuid or name")
            return None, None


def detect(filename):

    def builder(parser):
        @native
        def entity(name, attributes):
            if name == u"Type":
                parser.complete(TYPE)
            if name == u"Application":
                parser.complete(APPLICATION)
            else:
                parser.abort()
        return entity

    try:
        file = managers.file_manager.open(file_access.FILE, None, filename, mode="rb")
    except Exception as error:
        console.error("unable to open file: %s" % error)
        return None
    else:
        with closing(file):
            try:
                entity = Parser(builder=builder, supress=True).parse(file=file)
                if entity is TYPE:
                    return entity
                elif entity is APPLICATION:
                    return entity
                else:
                    console.error("file does not contain application or type")
                    return None
            except Exception as error:
                console.error("unable to detect %s contents: %s" % (filename, error))
                return None


def search_object(identifier):
    for application in managers.memory.applications.itervalues():
        if identifier == application.id:
            return application
        else:
            subject = application.objects.catalog.get(identifier)
            if subject is not None:
                return subject
    return None


def search_action(identifier):
    for application in managers.memory.applications.itervalues():
        subject = application.actions.catalog.get(identifier)
        if subject is not None:
            return subject
    return None

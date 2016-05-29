
from contextlib import closing
import managers
import file_access
from logs import console
from utils.parsing import Parser


TYPE = "type"
APPLICATION = "application"


def run(filename):
    """
    install application or type
    :param filename: input file with application or type
    """

    def builder(parser):
        def document_handler(name, attributes):
            if name == u"Type":
                parser.complete(TYPE)
            if name == u"Application":
                parser.complete(APPLICATION)
            else:
                parser.abort()
        return document_handler

    try:
        file = managers.file_manager.open(file_access.FILE, file_access.NO_OWNER, filename, mode="rb")
    except Exception as error:
        console.error("unable to open file: %s" % error)
    else:
        with closing(file):
            try:
                entity = Parser(builder=builder, supress=True).parse(file=file)
                if entity is TYPE:
                    console.write("install type from %s" % filename)
                    subject = managers.memory.install_type(filename)
                elif entity is APPLICATION:
                    console.write("install application from %s" % filename)
                    subject = managers.memory.install_application(filename)
                else:
                    console.error("file does not contain application or type")
                    return
            except Exception as error:
                console.error("unable to install %s: %s" % (entity, error))
                raise
            else:
                console.write("contains %s:%s" % (subject.id, subject.name.lower()))

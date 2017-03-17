
import settings

from logs import server_log
from utils.properties import aroproperty
from utils.tracing import format_exception_trace, show_exception_trace
from engine.exceptions import RenderTermination
from .constants import SOURCE_CODE, LISTING
from .properties import source_code_property, subsystem_lazy_property, bytecode_lazy_property
from .bytecode import ErrorBytecode


class Executable(object):

    scripting_language = aroproperty()
    package = aroproperty()
    signature = aroproperty()

    subsystem = subsystem_lazy_property()
    source_code = source_code_property()
    bytecode = bytecode_lazy_property()

    def locate(self, entity):
        return None

    def cleanup(self, remove=False):
        with self.lock:
            if remove:
                del self.source_code
            self.subsystem.cleanup(self)
            self.__dict__.pop("bytecode", None)

    def _compile(self):
        try:
            extension = self.subsystem.extensions.get(LISTING)
            if extension:
                if settings.STORE_BYTECODE:
                    location = self.locate(LISTING)
                    if location:
                        signature = location + extension
                    else:
                        signature = None
                else:
                    signature = None
            else:
                location = self.locate(SOURCE_CODE)
                if location:
                    signature = location + self.subsystem.source_extension
                else:
                    signature = None

            return self.subsystem.compile(self, signature)
        except Exception as error:
            if isinstance(error, SyntaxError):
                server_log.error("Unable to compile %s, line %s: %s" % (self, error.lineno, error.msg))
            else:
                server_log.error("Unable to compile %s: %s" % (self, error))
            return ErrorBytecode(format_exception_trace())

    def compile(self):
        self.__dict__.pop("bytecode", None)
        return self.bytecode

    def execute(self, context=None, namespace=None, arguments=None):
        if namespace is None:
            namespace = {}

        package = self.package
        if package:
            __import__(package)
            namespace["__package__"] = package

        try:
            self.bytecode.execute(context, namespace, arguments)
        except RenderTermination:
            raise
        except Exception:
            show_exception_trace(caption="Unhandled exception in %s" % self)
            raise

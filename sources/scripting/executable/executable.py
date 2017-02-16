
import settings

from logs import server_log
from utils.properties import aroproperty, lazy, roproperty
from utils.tracing import format_exception_trace, show_exception_trace
from engine.exceptions import RenderTermination
from .constants import SOURCE_CODE, LISTING
from .subsystems import select
from .properties import source_code_property


class Executable(object):

    @lazy
    def _subsystem(self):
        return select(self.scripting_language)

    @lazy
    def _bytecode(self):
        with self.lock:
            value = self._subsystem.restore(self) if settings.STORE_BYTECODE else None
            if value is None:
                value = self.compile()
            return value

    _traceback = None

    scripting_language = aroproperty()
    package = aroproperty()
    signature = aroproperty()

    subsystem = roproperty("_subsystem")

    source_code = source_code_property()
    bytecode = roproperty("_bytecode")
    traceback = roproperty("_traceback")

    def locate(self, entity):
        return None

    def cleanup(self, remove=False):
        with self.lock:
            if remove:
                del self.source_code
            self.subsystem.cleanup(self)
            self.__dict__.pop("_traceback", None)

    def compile(self):
        with self.lock:
            try:
                extension = self._subsystem.extensions.get(LISTING)
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
                        signature = location + self._subsystem.source_extension
                    else:
                        signature = None

                value = self.subsystem.compile(self, signature)
                self._bytecode = value
            except Exception as error:
                if isinstance(error, SyntaxError):
                    server_log.error("Unable to compile %s, line %s: %s" % (self, error.lineno, error.msg))
                else:
                    server_log.error("Unable to compile %s: %s" % (self, error))
                self._traceback = format_exception_trace()
                return None
            else:
                self._traceback = None
                return value

    def execute(self, context=None, namespace=None, arguments=None):
        if self._traceback:
            server_log.error(self._traceback)
        else:
            if namespace is None:
                namespace = {}

            package = self.package
            bytecode = self._bytecode

            if package:
                __import__(package)
                namespace["__package__"] = package

            try:
                bytecode.execute(context, namespace, arguments)
            except RenderTermination:
                raise
            except Exception:
                show_exception_trace(caption="Unhandled exception in %s" % self)
                raise

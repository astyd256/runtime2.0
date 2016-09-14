
import settings
from logs import server_log
from utils.properties import lazy, roproperty
from utils.tracing import format_exception_trace, show_exception_trace
from engine.exceptions import RenderTermination
from .constants import SOURCE_CODE, BYTECODE, TRACEBACK
from .subsystems import select


MISSING = "MISSING"


class Executable(object):

    @lazy
    def _subsystem(self):
        return select(self.scripting_language)

    def _get_source_code(self):
        with self.lock:
            return self.read(SOURCE_CODE)

    def _set_source_code(self, value):
        with self.lock:
            self.write(SOURCE_CODE, value)
            self.delete(BYTECODE)
            self.subsystem.cleanup(self)
            self.compile()

    subsystem = roproperty("_subsystem")
    source_code = property(_get_source_code, _set_source_code)

    def cleanup(self, source_code=False):
        if source_code:
            self.delete(SOURCE_CODE)
        self.delete(BYTECODE)
        self.subsystem.cleanup(self)

    def compile(self):
        with self.lock:
            source_code = self.read(SOURCE_CODE)
            try:
                bytecode = self.subsystem.compile(self, self.package, self.signature, source_code)
                traceback = None
            except SyntaxError as error:
                server_log.error("Unable to compile %s, line %s: %s" % (self, error.lineno, error.msg))
                bytecode = None
                traceback = format_exception_trace()
            except Exception as error:
                server_log.error("Unable to compile %s: %s" % (self, error))
                bytecode = None
                traceback = format_exception_trace()

            setattr(self, BYTECODE, bytecode)
            if bytecode is None:
                setattr(self, TRACEBACK, traceback)
            elif settings.STORE_BYTECODE:
                self.write(BYTECODE, bytecode)

    def execute(self, context=None, namespace=None):
        with self.lock:
            try:
                bytecode = getattr(self, BYTECODE)
            except AttributeError:
                bytecode = self.read(BYTECODE) if settings.STORE_BYTECODE else None
                if bytecode is None:
                    self.compile()
                    bytecode = getattr(self, BYTECODE)

            if bytecode is None:
                traceback = getattr(self, TRACEBACK)
                server_log.error(traceback)
                return

        if namespace is None:
            namespace = {}

        if self.package:
            __import__(self.package)
            namespace["__package__"] = self.package

        try:
            self.subsystem.execute(self, bytecode, context, namespace)
        except RenderTermination:
            raise
        except Exception:
            show_exception_trace(caption="Unhandled exception in %s" % self)
            raise

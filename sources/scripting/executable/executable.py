
import settings
import managers
import file_access

from logs import server_log
from utils.properties import aroproperty
from utils.tracing import format_exception_trace, show_exception_trace
from engine.exceptions import RenderTermination
from .constants import SOURCE_CODE, LISTING
from .subsystems import select
from .bytecode import ErrorBytecode
from .exceptions import SourceSyntaxError


class Executable(object):

    class SubsystemLazyProperty(object):

        def __get__(self, instance, owner=None):
            with instance.lock:
                instance.subsystem = value = select(instance.scripting_language)
                return value

    class SourceCodeProperty(object):

        __slots__ = "_handler"

        def __init__(self, handler=None):
            self._handler = handler

        def __get__(self, instance, owner=None):
            with instance.lock:
                try:
                    return instance._source_code
                except AttributeError:
                    location = instance.locate(SOURCE_CODE)
                    if location:
                        value = managers.file_manager.read(file_access.FILE, None,
                            location + instance.subsystem.source_extension, encoding="utf8", default=u"")
                    else:
                        value = u""
                    instance._source_code = value
                    return value

        def __set__(self, instance, value):
            with instance.lock:
                instance._source_code = value
                location = instance.locate(SOURCE_CODE)
                if location:
                    managers.file_manager.write(file_access.FILE, None,
                        location + instance.subsystem.source_extension, value, encoding="utf8")
                instance.cleanup()
                if self._handler:
                    self._handler(instance, value)

        def __delete__(self, instance):
            with instance.lock:
                instance._source_code = u""
                location = instance.location + instance.subsystem.source_extension
                if location:
                    managers.file_manager.delete(file_access.FILE, None, location)

    class BytecodeLazyProperty(object):

        def __get__(self, instance, owner=None):
            with instance.lock:
                instance.bytecode = value = \
                    (instance.subsystem.restore(instance) if settings.STORE_BYTECODE else None) or instance._compile()
                return value

    scripting_language = aroproperty()
    package = aroproperty()
    signature = aroproperty()

    subsystem = SubsystemLazyProperty()
    source_code = SourceCodeProperty()
    bytecode = BytecodeLazyProperty()

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
            message = "Unable to compile %s" % self
            if isinstance(error, SourceSyntaxError):
                details = "%s\nError on line %s: %s" % (message, error.lineno, error)
            else:
                details = format_exception_trace(caption=message, locals=True)
            return ErrorBytecode(message, details)

    def compile(self):
        self.__dict__.pop("bytecode", None)
        bytecode = self.bytecode
        bytecode.explain()
        return bytecode

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
            show_exception_trace(caption="Unhandled exception in %s" % self, locals=True)
            raise

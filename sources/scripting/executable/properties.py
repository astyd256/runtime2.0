
import managers
import file_access

from .constants import SOURCE_CODE


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
                        location + instance._subsystem.source_extension, encoding="utf8", default=u"")
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
                    location + instance._subsystem.source_extension, value, encoding="utf8")
            instance.cleanup()
            if self._handler:
                self._handler(instance, value)

    def __delete__(self, instance):
        with instance.lock:
            instance._source_code = u""
            location = instance.location + instance._subsystem.source_extension
            if location:
                managers.file_manager.delete(file_access.FILE, None, location)


source_code_property = SourceCodeProperty

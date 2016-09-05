
import managers
from utils.properties import lazy
from memory import PYTHON_LANGUAGE
from .constants import SOURCE_CODE
from .storage import Storage
from .generic import Executable


class ActionStorage(Storage):

    def exists(self, entity):
        return entity is SOURCE_CODE

    def read(self, entity):
        if entity is SOURCE_CODE:
            return self._source_code_value
        else:
            return None

    def write(self, entity, value):
        if entity is SOURCE_CODE:
            self._source_code_value = value

    def delete(self, entity):
        pass


class ActionExecutable(Executable):

    @lazy
    def scripting_language(self):
        return str(self.application.scripting_language)

    @lazy
    def package(self):
        return str(self.application.id)

    @lazy
    def signature(self):
        return "<%s action %s:%s>" % (self.scripting_language, self.id, self.name.lower())

    def execute(self, context=None, namespace=None):
        if self.scripting_language == PYTHON_LANGUAGE:
            return super(ActionExecutable, self).execute(context=context, namespace=namespace)
        else:
            if namespace is None:
                namespace = managers.request_manager.get_request().session().context
            with self.lock:
                return super(ActionExecutable, self).execute(context=context,
                    namespace=namespace)

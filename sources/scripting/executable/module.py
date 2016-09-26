
import managers
import file_access

from utils.properties import lazy
from utils.statistics import statistics
from memory import PYTHON_LANGUAGE

from ..object import VDOMObject
from .constants import LISTING
from .storage import FileStorage
from .generic import Executable


class ModuleStorage(FileStorage):

    def locate(self, entity):
        return managers.file_manager.locate(file_access.MODULE,
            self.id, self.name) + self.subsystem.extensions[entity]

    # def read(self, entity):
    #     statistics.increase("module.read")
    #     return super(ModuleStorage, self).read(entity)


class ModuleExecutable(Executable):

    @lazy
    def scripting_language(self):
        return PYTHON_LANGUAGE

    @lazy
    def package(self):
        return None

    @lazy
    def signature(self):
        return self.locate(LISTING) or "<%s module %s:%s>" % (self.scripting_language, self.id, self.name.lower())

    def execute(self, context=None, namespace=None):
        # statistics.increase("module.execute")
        if self.scripting_language == PYTHON_LANGUAGE:
            if namespace is None:
                namespace = {}
            namespace.update(VDOMObject=VDOMObject, VDOM_object=VDOMObject)
        return super(ModuleExecutable, self).execute(context=context, namespace=namespace)

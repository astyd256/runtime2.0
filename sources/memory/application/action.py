
import settings
import managers
import file_access

from uuid import uuid4
from utils.properties import weak, constant, roproperty, rwproperty
from utils import verificators
from scripting.executable import source_code_property, SOURCE_CODE, Executable

from ..constants import PYTHON_LANGUAGE
from ..auxiliary import UNAVAILABLE_SELF
from ..generic import MemoryBase


@weak("_collection", "_owner")
class MemoryActionSketch(MemoryBase, Executable):

    is_action = constant(True)
    is_binding = constant(False)

    _restore = False

    _id = None
    _name = None
    _top = 0
    _left = 0
    _state = False
    _source_code = u""

    def __init__(self, collection, handler=None):
        self._collection = collection
        self._owner = collection.owner
        self._handler = handler

    lock = property(lambda self: self._owner.lock)
    owner = target_object = roproperty("_owner")
    application = property(lambda self: self._owner.application)

    scripting_language = property(lambda self: str(self._owner.application.scripting_language))
    package = property(lambda self: str(self._owner.application.id))
    signature = property(lambda self: "<%s action %s:%s>" % (self.scripting_language, self.id, self.name.lower()))

    id = rwproperty("_id")
    name = rwproperty("_name")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")
    handler = rwproperty("_handler")

    source_code = rwproperty("_source_code")

    def __invert__(self):
        restore = self._restore
        self.__class__ = MemoryAction
        self._collection.on_complete(self, restore)

        if self._id is None:
            raise Exception(u"Action require identifier")
        if self._name is None:
            raise Exception(u"Action require name")

        return self

    def __str__(self):
        return " ".join(filter(None, (
            "action",
            "\"%s\"" % self._name if self._name else None,
            "sketch of %s" % self._owner)))


class MemoryActionRestorationSketch(MemoryActionSketch):

    _restore = True


class MemoryActionDuplicationSketch(MemoryActionSketch):

    def __init__(self, collection, another, handler=None):
        self._collection = collection
        self._owner = collection.owner
        self._handler = handler
        self._id = str(uuid4())
        self._name = another._name
        self._top = another._top
        self._left = another._left
        self._state = another._state
        self._source_code = another._source_code


class MemoryAction(MemoryActionSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new action")

    def _set_name(self, value):
        if self._name == value:
            return

        if not verificators.name(value):
            raise Exception("Invalid name: %r" % value)

        with self._owner.lock:
            self._name, value = self._collection.on_rename(self, value), self._name
            self._owner.invalidate(contexts=(self._id, self._name, value), downward=True, upward=True)
            self._owner.autosave()

    def _set_top(self, value):
        self._top = value
        self._owner.autosave()

    def _set_left(self, value):
        self._left = value
        self._owner.autosave()

    def _set_state(self, value):
        self._state = value
        self._owner.autosave()

    id = roproperty("_id")
    name = rwproperty("_name", _set_name)
    top = rwproperty("_top", _set_top)
    left = rwproperty("_left", _set_left)
    state = rwproperty("_state", _set_state)
    handler = roproperty("_handler")

    def locate(self, entity):
        if entity is not SOURCE_CODE and not self._owner.virtual \
                and settings.STORE_BYTECODE and settings.STORE_ACTIONS_BYTECODE:
            return managers.file_manager.locate(file_access.CACHE, self._owner.application.id, self._id)
        else:
            return None

    @source_code_property
    def source_code(self, value):
        self._owner.invalidate(contexts=(self._id, self._name), downward=True, upward=True)
        self._owner.autosave()

    def execute(self, context=None, namespace=None, arguments=None):
        if self._handler:
            self._handler.execute(context, namespace,
                arguments={
                    "self": UNAVAILABLE_SELF,
                    "source_object": context,
                    "action_name": self._name,
                    "source_code": self.source_code})
        else:
            # statistics.increase("action.execute")
            if self.scripting_language == PYTHON_LANGUAGE:
                return super(MemoryAction, self).execute(context=context, namespace=namespace, arguments=arguments)
            else:
                if namespace is None:
                    namespace = managers.request_manager.get_request().session().context
                with self.lock:
                    return super(MemoryAction, self).execute(context=context, namespace=namespace, arguments=arguments)

    # unsafe
    def compose(self, ident=u"", file=None):
        information = u"ID=\"%s\" Name=\"%s\" Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._id, self._name.encode("xml"), self._top, self._left, self._state)
        if self.source_code:
            file.write(u"%s<Action %s>\n" % (ident, information))
            file.write(u"%s\n" % self.source_code.encode("cdata"))
            file.write(u"%s</Action>\n" % ident)
        else:
            file.write(u"%s<Action %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, (
            "action",
            "%s:%s" % (self._id, self._name) if self._name else None,
            "of %s" % self._owner)))

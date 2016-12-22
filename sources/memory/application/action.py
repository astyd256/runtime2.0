
from uuid import uuid4
from utils.properties import lazy, constant, roproperty, rwproperty
from utils import verificators
from scripting.executable import ActionStorage, ActionExecutable
from ..generic import MemoryBase


class MemoryActionSketch(MemoryBase, ActionStorage, ActionExecutable):

    is_action = constant(True)
    is_binding = constant(False)

    def __init__(self, callback, owner):
        self._callback = callback
        self._owner = owner
        self._id = None
        self._name = None
        self._top = 0
        self._left = 0
        self._state = False
        self._source_code_value = u""

    lock = property(lambda self: self._owner.lock)
    owner = target_object = roproperty("_owner")
    application = property(lambda self: self._owner.application)

    id = rwproperty("_id")
    name = rwproperty("_name")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")
    source_code_value = rwproperty("_source_code_value")

    def __invert__(self):
        self.__class__ = MemoryAction
        self._callback = self._callback(self)

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


class MemoryActionDuplicationSketch(MemoryActionSketch):

    def __init__(self, callback, owner, another):
        self._callback = callback
        self._owner = owner
        self._id = str(uuid4())
        self._name = another._name
        self._top = another._top
        self._left = another._left
        self._state = another._state
        self._source_code_value = another._source_code_value


class MemoryAction(MemoryActionSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new action")

    def _set_name(self, value):
        if self._name == value:
            return

        if not verificators.name(value):
            raise Exception("Invalid name: %r" % value)

        with self._owner.lock:
            self._name = self._callback(self, value)
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

    def _get_source_code(self):
        with self._owner.lock:
            return super(MemoryAction, self)._get_source_code()

    def _set_source_code(self, value):
        with self._owner.lock:
            super(MemoryAction, self)._set_source_code(value)
            self._owner.invalidate(contexts=(self._id, self._name), downward=True, upward=True)
            self._owner.autosave()

    id = roproperty("_id")
    name = rwproperty("_name", _set_name)
    top = rwproperty("_top", _set_top)
    left = rwproperty("_left", _set_left)
    state = rwproperty("_state", _set_state)
    source_code = property(_get_source_code, _set_source_code)

    # unsafe
    def compose(self, ident=u"", file=None):
        information = u"ID=\"%s\" Name=\"%s\" Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._id, self._name.encode("xml"), self._top, self._left, self._state)
        if self.source_code:
            file.write(u"%s<Action %s>\n" % (ident, information))
            file.write(u"%s\n" % self.source_code_value.encode("cdata"))
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

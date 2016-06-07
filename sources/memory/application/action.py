
from uuid import uuid4
from utils.properties import lazy, constant, roproperty, rwproperty
from ..generic import MemoryBase


class MemoryActionSketch(MemoryBase):

    is_action = constant(True)
    is_binding = constant(False)

    @lazy
    def _executable(self):
        from scripting.executable import select_action_class
        return select_action_class(self._owner.application.scripting_language)(self, self._name)

    def __init__(self, callback, owner):
        self._callback = callback
        self._owner = owner
        self._id = None
        self._name = None
        self._top = 0
        self._left = 0
        self._state = False
        self._source_code = u""

    owner = roproperty("_owner")
    application = roproperty("_owner.application")

    id = rwproperty("_id")
    name = rwproperty("_name")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")
    source_code = rwproperty("_source_code")

    def __invert__(self):
        if self._id is None:
            raise Exception(u"Action require identifier")
        if self._name is None:
            raise Exception(u"Action require name")

        self.__class__ = MemoryAction
        self._callback = self._callback(self)
        return self

    def __str__(self):
        return " ".join(filter(None, (
            "action",
            repr(self._name) if self._name else None,
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
        self._source_code = another._source_code


class MemoryAction(MemoryActionSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new action")

    def _set_name(self, value):
        with self._owner.lock:
            if self._name != value:
                contexts = self._id, self._name, value
                self._callback(self, value)
                self._name = value
                self._owner.invalidate(contexts=contexts, downward=True, upward=True)
                self._owner.autosave()

    def _set_source_code(self, value):
        with self._owner.lock:
            self._source_code = value
            if "_executable" in self.__dict__:
                del self._executable
            self._owner.invalidate(contexts=(self._id, self._name), downward=True, upward=True)
            self._owner.autosave()

    id = roproperty("_id")
    name = rwproperty("_name", _set_name)
    top = rwproperty("_top", notify="_owner.autosave")
    left = rwproperty("_left", notify="_owner.autosave")
    state = rwproperty("_state", notify="_owner.autosave")
    source_code = rwproperty("_source_code", _set_source_code)

    # unsafe
    def compose(self, ident=u"", file=None):
        information = u"ID=\"%s\" Name=\"%s\" Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._id, self._name.encode("xml"), self._top, self._left, self._state)
        if self._source_code:
            file.write(u"%s<Action %s>\n" % (ident, information))
            file.write(u"%s\n" % self._source_code.encode("cdata"))
            file.write(u"%s</Action>\n" % ident)
        else:
            file.write(u"%s<Action %s/>\n" % (ident, information))

    # unsafe
    def execute(self, object, namespace):
        if self._source_code:
            self._executable.execute(namespace, context=object, sandbox=True)

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, (
            "action",
            repr(self._name) if self._name else None,
            "of %s" % self._owner)))

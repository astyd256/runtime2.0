
from utils.properties import weak, roproperty, rwproperty
from ..generic import MemoryBase
from .eventcallees import MemoryEventCalleesSketch


@weak("_collection")
class MemoryEventSketch(MemoryBase):

    _restore = False

    _top = 0
    _left = 0
    _state = False

    def __init__(self, collection, owner, name):
        self._collection = collection
        self._owner = owner
        self._name = name
        self._callees = MemoryEventCalleesSketch(self)

    owner = roproperty("_owner")
    container = property(lambda self: self._owner.container)

    source_object = roproperty("_owner")
    name = rwproperty("_name")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")
    callees = roproperty("_callees")

    def __invert__(self):
        ~self._callees
        restore = self._restore
        self.__class__ = MemoryEvent
        self._collection.on_complete(self, restore)
        return self

    def __str__(self):
        return " ".join(filter(None, (
            "event",
            "\"%s\"" % self._name if self._name else None,
            "sketch of %s" % self._owner)))


class MemoryEventRestorationSketch(MemoryEventSketch):

    _restore = True


class MemoryEvent(MemoryEventSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new event")

    def _set_name(self, value):
        self._name = value
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

    name = rwproperty("_name", _set_name)
    top = rwproperty("_top", _set_top)
    left = rwproperty("_left", _set_left)
    state = rwproperty("_state", _set_state)

    # unsafe
    def compose(self, ident=u"", file=None):
        information = u"ContainerID=\"%s\" ObjSrcID=\"%s\" Name=\"%s\" Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._owner.container.id, self._owner.id, self._name, self._top, self._left, self._state)
        if self._callees:
            file.write(u"%s<Event %s>\n" % (ident, information))
            for callee in self._callees:
                file.write(u"%s\t<Action ID=\"%s\"/>\n" % (ident, callee.id))
            file.write(u"%s</Event>\n" % ident)
        else:
            file.write(u"%s<Event %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, (
            "event",
            "\"%s\"" % self._name if self._name else None,
            "of %s" % self._owner)))

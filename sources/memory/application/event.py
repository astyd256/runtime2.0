
from utils.properties import roproperty, rwproperty
from ..generic import MemoryBase
from .eventcallees import MemoryEventCalleesSketch


class MemoryEventSketch(MemoryBase):

    def __init__(self, callback, owner, name):
        self._callback = callback
        self._owner = owner

        self._name = name
        self._top = 0
        self._left = 0
        self._state = False

        self._callees = MemoryEventCalleesSketch(self)

    owner = roproperty("_owner")
    container = roproperty("_owner.container")

    source_object = roproperty("_owner")
    name = rwproperty("_name")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")
    callees = roproperty("_callees")

    def __invert__(self):
        ~self._callees
        self.__class__ = MemoryEvent
        self._callback = self._callback(self)
        return self

    def __str__(self):
        return " ".join(filter(None, (
            "event",
            "\"%s\"" % self._name if self._name else None,
            "sketch of %s" % self._owner)))


class MemoryEvent(MemoryEventSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new event")

    name = rwproperty("_name", notify="_owner.autosave")
    top = rwproperty("_top", notify="_owner.autosave")
    left = rwproperty("_left", notify="_owner.autosave")
    state = rwproperty("_state", notify="_owner.autosave")

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

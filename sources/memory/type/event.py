
from utils.properties import roproperty, rwproperty
from ..generic import MemoryBase
from .eventparameters import MemoryTypeEventParameters


class MemoryTypeEventSketch(MemoryBase):

    _name = None
    _description = u""

    def __init__(self, callback, owner):
        self._callback = callback
        self._owner = owner
        self._parameters = MemoryTypeEventParameters(self)

    owner = roproperty("_owner")

    name = rwproperty("_name")
    description = rwproperty("_description")
    parameters = roproperty("_parameters")

    def __invert__(self):
        if self._name is None:
            raise Exception(u"Event require name")

        self.__class__ = MemoryTypeEvent
        self._callback = self._callback(self)
        return self

    def __str__(self):
        return " ".join(filter(None, ("event", self._name, "sketch of %s" % self._owner)))


class MemoryTypeEvent(MemoryTypeEventSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new event")

    name = roproperty("_name")
    description = roproperty("_description")
    parameters = roproperty("_parameters")

    def compose(self, ident=u"", file=None):
        information = u"Name=\"%s\" Description=\"%s\"" % \
            (self._name, self._description.encode("xml"))
        if self._parameters:
            file.write(u"%s<Event %s>\n" % (ident, information))
            self._parameters.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Event>\n" % ident)
        else:
            file.write(u"%s<Event %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, ("event", self._name, "of %s" % self._owner)))

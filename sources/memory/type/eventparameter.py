
from utils.properties import roproperty, rwproperty
from ..generic import MemoryBase


class MemoryTypeEventParameterSketch(MemoryBase):

    _name = None
    _description = u""
    _order = 0

    def __init__(self, callback, owner):
        self._callback = callback
        self._owner = owner

    owner = roproperty("_owner")

    name = rwproperty("_name")
    description = rwproperty("_description")
    order = rwproperty("_order")

    def __invert__(self):
        if self._name is None:
            raise Exception(u"Event parameter require name")

        self.__class__ = MemoryTypeEventParameter
        self._callback = self._callback(self)
        return self

    def __str__(self):
        return " ".join(filter(None, ("parameter", self._name, "sketch of %s" % self._owner)))


class MemoryTypeEventParameter(MemoryTypeEventParameterSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new parameter")

    name = roproperty("_name")
    description = roproperty("_description")
    order = roproperty("_order")

    def compose(self, ident=u"", file=None):
        file.write(u"%s<Parameter Name=\"%s\" Description=\"%s\" Order=\"%s\"/>\n" %
            (ident, self._name, self._description.encode("xml"), self._order))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, ("parameter", self._name, "of %s" % self._owner)))


from utils.properties import roproperty, rwproperty
from ..generic import MemoryBase
from .actionparameters import MemoryTypeActionParameters


class MemoryTypeActionSketch(MemoryBase):

    def __init__(self, callback, owner):
        self._callback = callback
        self._owner = owner
        self._scope = None
        self._name = None
        self._display_name = None
        self._description = u""
        self._source_code = u""
        self._parameters = MemoryTypeActionParameters(self)

    owner = roproperty("_owner")

    scope = rwproperty("_scope")
    name = rwproperty("_name")
    display_name = rwproperty("_display_name")
    description = rwproperty("_description")
    source_code = rwproperty("_source_code")
    parameters = roproperty("_parameters")

    def __invert__(self):
        if self._scope is None:
            raise Exception(u"Type action require scope")
        if self._name is None:
            raise Exception(u"Type action require name")

        if self._display_name is None:
            self._display_name = self._name

        self.__class__ = MemoryTypeAction
        self._callback = self._callback(self)
        return self

    def __str__(self):
        return " ".join(filter(None, ("action", "\"%s\"" % self._name, "sketch of %s" % self._owner)))


class MemoryTypeAction(MemoryTypeActionSketch):

    def __init__(self):
        raise Exception("User 'new_sketch' to create action")

    scope = roproperty("_scope")
    name = roproperty("_name")
    display_name = roproperty("_display_name")
    description = roproperty("_description")
    source_code = roproperty("_source_code")
    parameters = roproperty("_parameters")

    # unsafe
    def compose(self, ident=u"", file=None):
        file.write(u"%s<Action Name=\"%s\" DisplayName=\"%s\" Description=\"%s\">\n" %
            (ident, self._name, self._display_name.encode("xml"), self._description.encode("xml")))
        self._parameters.compose(ident=ident + u"\t", file=file)
        file.write(u"%s\t<SourceCode>\n" % ident)
        file.write(u"%s\n" % self._source_code.strip().encode("cdata"))
        file.write(u"%s\t</SourceCode>\n" % ident)
        file.write(u"%s</Action>\n" % ident)

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, ("action", "\"%s\"" % self._name, "of %s" % self._owner)))

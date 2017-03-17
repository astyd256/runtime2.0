
import re
from utils.properties import lazy, weak, roproperty, rwproperty
from ..generic import MemoryBase


@weak("_collection")
class MemoryTypeActionParameterSketch(MemoryBase):

    @lazy
    def _regex(self):
        return re.compile("^%s$" % self._validation_pattern)

    _name = None
    _display_name = u""
    _description = u""
    _default_value = u""
    _validation_pattern = u".*"
    _interface = u""

    def __init__(self, collection):
        self._collection = collection

    def _set_validation_pattern(self, value):
        self._validation_pattern = value
        self.__dict__.pop("_regex", None)

    owner = property(lambda self: self._collection.owner)

    name = rwproperty("_name")
    display_name = rwproperty("_display_name")
    description = rwproperty("_description")
    default_value = rwproperty("_default_value")
    validation_pattern = rwproperty("_validation_pattern", _set_validation_pattern)
    interface = rwproperty("_interface")

    def __invert__(self):
        if self._name is None:
            raise Exception(u"Parameter require name")

        self.__class__ = MemoryTypeActionParameter
        self._collection.on_complete(self)
        return self

    def __str__(self):
        return " ".join(filter(None, ("parameter", "\"%s\"" % self._name,
            "sketch of %s" % self._collection.owner if self._collection else None)))


class MemoryTypeActionParameter(MemoryTypeActionParameterSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new parameter")

    name = roproperty("_name")
    display_name = roproperty("_display_name")
    description = roproperty("_description")
    default_value = roproperty("_default_value")
    validation_pattern = roproperty("_validation_pattern")
    interface = roproperty("_interface")

    # unsafe
    def compose(self, ident=u"", file=None):
        file.write(u"%s<Parameter Name=\"%s\" DisplayName=\"%s\" Description=\"%s\" "
            "DefaultValue=\"%s\" RegularExpressionValidation=\"%s\" Interface=\"%s\" />\n" %
            (ident, self._name, self._display_name.encode("xml"), self._description.encode("xml"),
                self._default_value.encode("xml"), self._validation_pattern.encode("xml"), self._interface.encode("xml")))

    def verify(self, value):
        return self._regex.match(value) is not None

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, ("parameter", "\"%s\"" % self._name,
            "of %s" % self._collection.owner if self._collection else None)))


from utils.properties import constant, roproperty, rwproperty
from ..generic import MemoryBase
from .bindingparameters import MemoryBindingParameters


class MemoryBindingSketch(MemoryBase):

    is_action = constant(False)
    is_binding = constant(True)

    def __init__(self, callback, target_object, name, parameters=None):
        self._callback = callback
        self._id = None
        self._target_object = target_object
        self._name = name
        self._top = 0
        self._left = 0
        self._state = False
        self._parameters = MemoryBindingParameters(self, parameters)

    id = rwproperty("_id")
    target_object = roproperty("_target_object")
    name = roproperty("_name")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")
    parameters = roproperty("_parameters")

    def __invert__(self):
        self.__class__ = MemoryBinding
        self._callback = self._callback(self)
        return self

    def __str__(self):
        return " ".join(filter(None, (
            "binding",
            repr(self._name) if self._name else None,
            "sketch of %s" % self._target_object)))


class MemoryBinding(MemoryBindingSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new binding")

    id = roproperty("_id")
    target_object = roproperty("_target_object")
    name = roproperty("_name")
    top = rwproperty("_top", notify="_target_object.autosave")
    left = rwproperty("_left", notify="_target_object.autosave")
    state = rwproperty("_state", notify="_target_object.autosave")
    parameters = roproperty("_parameters")

    # unsafe
    def compose(self, ident=u"", file=None):
        information = u"ID=\"%s\" ObjTgtID=\"%s\" Name=\"%s\" Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._id, self._target_object.id, self._name, self._top, self._left, self._state)
        if self._parameters:
            file.write(u"%s<Action %s>\n" % (ident, information))
            for name, value in self._parameters.iteritems():
                file.write(u"%s\t<Parameter Name=\"%s\">%s</Parameter>\n" % (ident, name, value.encode("xml")))
            file.write(u"%s</Action>\n" % ident)
        else:
            file.write(u"%s<Action %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, (
            "binding",
            repr(self._name) if self._name else None,
            "of %s" % self._target_object)))

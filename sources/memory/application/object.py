
from weakref import WeakValueDictionary

import managers

from logs import log
from utils.properties import lazy, weak, constant, roproperty, rwproperty
from utils import verificators

from ..constants import NON_CONTAINER, CONTAINER, TOP_CONTAINER, RENDER_CONTEXT
from ..generic import MemoryBase

from .attributes import MemoryAttributesSketch
from .actions import MemoryActions
from .events import MemoryEvents
from .structure import MemoryStructureSketch, MemoryStructure


@weak("_parent", "_application")
class MemoryObjectSketch(MemoryBase):

    is_application = constant(False)
    is_object = constant(True)

    is_non_container = property(lambda self: self._type.container == NON_CONTAINER)
    is_container = property(lambda self: CONTAINER <= self._type.container <= TOP_CONTAINER)
    is_top_container = property(lambda self: self._type.container == TOP_CONTAINER)

    generic = RENDER_CONTEXT,

    @lazy
    def _container(self):
        return self._parent._container if self._parent else self

    @lazy
    def _dependents(self):
        return set()

    @lazy
    def _classes(self):
        return WeakValueDictionary()

    @lazy
    def _structure(self):
        return None if self._parent or self._virtual else MemoryStructureSketch(self)

    def __init__(self, callback, type, application, parent, virtual=False, attributes=None):
        self._callback = callback
        self._order = None
        self._virtual = virtual
        self._application = application
        self._parent = parent

        # generic characteristics
        self._type = type
        self._id = None
        self._name = None

        # collections
        self._attributes = MemoryAttributesSketch(self, attributes=attributes)
        self._objects = MemoryObjects(self)
        self._events = MemoryEvents(self)
        self._actions = MemoryActions(self)

    lock = property(lambda self: self._application.lock)
    order = rwproperty("_order")
    is_virtual = virtual = roproperty("_virtual")
    application = rwproperty("_application")
    container = roproperty("_container")
    parent = rwproperty("_parent")

    type = rwproperty("_type")
    id = rwproperty("_id")
    name = rwproperty("_name")

    attributes = roproperty("_attributes")
    objects = roproperty("_objects")
    events = roproperty("_events")
    actions = roproperty("_actions")

    structure = roproperty("_structure")

    stateful = property(lambda self: int(self._attributes.get("stateful", 0)))
    hierarchy = property(lambda self: int(self._attributes.get("hierarchy", 0)))

    def __invert__(self):
        ~self._attributes
        if self.__dict__.get("_structure") is not None:
            ~self._structure

        self.__class__ = MemoryObject
        self._callback = self._callback(self)

        if self.id is None:
            raise Exception(u"Object require identifier")
        if self.name is None:
            raise Exception(u"Object require name")

        return self

    def __str__(self):
        return " ".join(filter(None, (
            "virtual" if getattr(self, "_virtual", None) else None,
            "object",
            ":".join(filter(None, (getattr(self, "_id", None), getattr(self, "_name", None)))),
            "sketch")))


class MemoryObjectDuplicationSketch(MemoryObjectSketch):

    def __init__(self, callback, application, parent, another):
        super(MemoryObjectDuplicationSketch, self).__init__(callback,
            another.type, application, parent,
            virtual=parent.virtual, attributes=another.attributes)
        self._objects += another.objects


class MemoryObject(MemoryObjectSketch):

    @lazy
    def _structure(self):
        return None if self._parent or self._virtual else MemoryStructure(self)

    def __init__(self):
        raise Exception(u"Use 'new' to create new object")

    def _set_name(self, value):
        if self._name == value:
            return

        if not verificators.name(value):
            raise Exception("Unacceptable value for %s name: %r" % (self, value))

        with self.lock:
            managers.dispatcher.dispatch_handler(self, "on_rename", value)
            self._callback(self, value)
            self._name = value
            self.invalidate(upward=True)
            self.autosave()

    type = roproperty("_type")
    id = roproperty("_id")
    name = rwproperty("_name", _set_name)

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False):
        information = u"ID=\"%s\" Name=\"%s\" Type=\"%s\"" % (self._id, self._name.encode("xml"), self._type.id)
        if self._attributes or self._objects or self._actions:
            file.write(u"%s<Object %s>\n" % (ident, information))
            self._attributes.compose(ident=ident + u"\t", file=file, shorter=shorter)
            self._objects.compose(ident=ident + u"\t", file=file, shorter=shorter)
            self._actions.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Object>\n" % ident)
        else:
            file.write(u"%s<Object %s/>\n" % (ident, information))

    def autosave(self):
        if not self._virtual:
            self._application.autosave()

    def invalidate(self, contexts=None, downward=False, upward=False):
        with self.lock:
            # cleanup compiled classes
            if "_classes" in self.__dict__:
                if contexts:
                    if isinstance(contexts, basestring):
                        log.write("Invalidate %s in %s context" % (self, contexts))
                        try:
                            del self._classes[contexts]
                        except KeyError:
                            log.write("Nothing to invalidate for %s in %s context" % (self, contexts))
                    else:
                        log.write("Invalidate %s in %s contexts" % (self, ", ".join(contexts)))
                        for context in contexts:
                            try:
                                del self._classes[context]
                            except KeyError:
                                log.write("Nothing to invalidate for %s in %s context" % (self, contexts))
                else:
                    log.write("Invalidate %s" % self)
                    self._classes = {}

            # cleanup resources
            # TODO: (!) this can delete compiled e2vdom scripts
            #       check necessity of resource invalidation
            #       possible this must be done on object delete
            managers.resource_manager.invalidate_resources(self._id)

            # perform downward invalidation
            if downward:
                for child in self._objects.itervalues():
                    child.invalidate(contexts=contexts, downward=True)

            # perform upward invalidation
            if upward:
                if self._parent:
                    self._parent.invalidate(contexts=contexts, upward=True)
                for dependent in self.__dict__.get("_dependents", ()):
                    log.write("Invalidate %s dependent %s" % (self, dependent))
                    dependent.invalidate(contexts=contexts, upward=True)

    def attach(self, object):
        with self.lock:
            self._dependents.add(object)

    def detach(self, object):
        with self.lock:
            self._dependents.remove(object)

    def factory(self, context, dynamic=None, probe=False):
        if dynamic is None:
            try:
                klass = self._classes[context]
            except KeyError:
                if probe:
                    return None
            else:
                if dynamic <= klass._dynamic:
                    return klass

        new_klass = managers.compiler.compile(self, context, dynamic=dynamic)

        with self.lock:
            klass = self._classes.get(context)
            if klass is None or dynamic > klass._dynamic:
                self._classes[context] = klass = new_klass
            return klass

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, (
            "virtual" if self._virtual else None,
            "object",
            ":".join(filter(None, (self._id, self._name))))))


from .objects import MemoryObjects

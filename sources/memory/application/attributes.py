
import re
from collections import Mapping, MutableMapping
import settings
import managers
from utils.properties import lazy, weak
from logs import log
from ..generic import MemoryBase


FORCE_CDATA_LENGTH = 1024
FORCE_CDATA_REGEX = re.compile(u"[\u0000-\u0019\"<=>]", re.MULTILINE)
DEREFERENCE_REGEX = re.compile(r"\#RES\(([A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})\)", re.IGNORECASE)


@weak("_owner")
class MemoryAttributesSketch(MemoryBase, MutableMapping):

    @lazy
    def _attributes(self):
        return self._owner.type.attributes

    @lazy
    def _cdata(self):
        return set()

    @lazy
    def _query(self):
        return set(self._items)

    def __init__(self, owner, attributes=None):
        self._owner = owner
        if attributes:
            self._items = {name: value for name, value in attributes.iteritems() if name in owner.type.attributes}
        else:
            self._items = {}

    def __getitem__(self, name):
        return self._items[name]

    def __setitem__(self, name, value):
        value = DEREFERENCE_REGEX.sub(lambda match: match.group(1), value)
        self._query.add(name)
        self._items[name] = value

    def __delitem__(self, name):
        del self._items[name]

    def __iter__(self):
        return iter(self._owner.type.attributes)

    def __len__(self):
        return len(self._owner.type.attributes)

    def __invert__(self):
        self.__class__ = MemoryAttributes
        return self

    def __str__(self):
        return "attributes sketch of %s" % self._owner


class MemoryAttributes(MemoryAttributesSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new attribute")

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False):
        if self._items:
            for name in self._query:
                value = self._items[name]
                cdata = len(value) > FORCE_CDATA_LENGTH or FORCE_CDATA_REGEX.search(value)
                if name in self._cdata:
                    if not cdata:
                        self._cdata.remove(name)
                else:
                    if cdata:
                        self._cdata.add(name)

            self._query.clear()

            file.write(u"%s<Attributes>\n" % ident)
            for name, value in self._items.iteritems():
                if not settings.STORE_DEFAULT_VALUES and \
                        value == self._owner.type.attributes[name].default_value:
                    continue
                complexity = self._owner.type.attributes[name].complexity or name in self._cdata
                file.write(u"%s\t<Attribute Name=\"%s\">%s</Attribute>\n" %
                    (ident, name, value.encode("cdata" if complexity else "xml")))
            file.write(u"%s</Attributes>\n" % ident)

    def update(self, *arguments, **keywords):
        if arguments:
            collection = arguments[0]
            if isinstance(collection, Mapping):
                attributes = collection
            elif hasattr(collection, "keys"):
                attributes = {key: collection[key] for key in collection.keys()}
            else:
                attributes = {key: collection[key] for key, value in collection}
        else:
            attributes = keywords

        updates = {}
        with self._owner.lock:
            for name, value in attributes.iteritems():
                try:
                    current_value = self._items[name]
                except KeyError:
                    try:
                        current_value = self._owner.type.attributes[name].default_value
                    except KeyError:
                        raise Exception("The object has no \"%s\" attribute " % name)

                if not isinstance(value, basestring):
                    value = str(value)

                value = DEREFERENCE_REGEX.sub(lambda match: match.group(1), value)

                if current_value != value:
                    if self._owner.type.attributes[name].verify(value):
                        updates[name] = value
                    else:
                        raise ValueError(u"Unacceptable value for \"%s\" attribute: \"%s\"" % (name, value.replace('"', '\"')))

            if updates:
                managers.dispatcher.dispatch_handler(self._owner, "on_update", updates)

                if updates:
                    for name, value in updates.iteritems():
                        if not isinstance(value, basestring):
                            value = str(value)

                        self._query.add(name)

                        log.write("Update %s attrbiute \"%s\" to \"%s\"" % (self._owner, name, value.replace('"', '\"')))
                        self._items[name] = value

                    self._owner.invalidate(upward=1)
                    self._owner.autosave()

    def __getitem__(self, name):
        try:
            return self._items[name]
        except KeyError:
            return self._owner.type.attributes[name].default_value

    def __setitem__(self, name, value):
        self.update({name: value})

    def __delitem__(self, name):
        managers.dispatcher.dispatch_handler(self._owner, "on_update", self._owner.type.attributes[name].default_value)
        log.write("Reset %s attrbiute \"%s\"" % (self._owner, name))
        self._items.pop(name, None)
        self._owner.invalidate(upward=1)
        self._owner.autosave()

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return "attributes of %s" % self._owner

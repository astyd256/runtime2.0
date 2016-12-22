
import json

from copy import copy
from collections import Mapping, MutableMapping

import managers

from logs import log
# from .wrappers import obsolete_request
from .compiler import STATE_UNMODIFIED, STATE_MODIFIED, \
    STATE_UP_TO_DATE, STATE_REQUIRE_RECOMPUTE, STATE_RECOMPUTE  # STATE_AVOID_RECOMPUTE
from .compiler.descriptors import make_attribute_name, make_object_name, make_descriptor_name


# class VDOMType(object):

#     def __init__(self, id, name, version):
#         self._id = id
#         self._name = name
#         self._version = version

#     id = property(lambda self: self.__class__._id)
#     name = property(lambda self: self.__class__._name)
#     version = property(lambda self: self.__class__._version)

#     def __call__(self, context, attributes=None):

#         def __init__(self, parent):
#             self._origin = None
#             self._action = None
#             self._context = context

#         klass = type("OBJECT", (VDOMObject,), {})
#         return klass


class VDOMObjectAttributes(MutableMapping):

    def __init__(self, owner):
        self._owner = owner

    def __getitem__(self, name):
        # return getattr(self._owner, make_attribute_name(name))
        return getattr(self._owner, make_descriptor_name(name))

    def __setitem__(self, name, value):
        # setattr(self._owner, make_attribute_name(name), value)
        setattr(self._owner, make_descriptor_name(name), value)

    def __delitem__(self, name):
        raise NotImplementedError

    def __iter__(self):
        for name in self._owner._attributes:
            yield getattr(self._owner, make_attribute_name(name))

    def __len__(self):
        return len(self._owner._attributes)


class VDOMObjectObjects(Mapping):

    def __init__(self, owner):
        self._owner = owner

    def __getitem__(self, name):
        try:
            return getattr(self._owner, make_object_name(name))
        except AttributeError:
            return self._owner._instantiate(name)

    def __iter__(self):
        return iter(self._owner._objects)

    def __len__(self):
        return len(self._owner._objects)


class VDOMObject(object):

    # attributes that initialized by the compiler at runtime

    # internal attributes
    #   _origin                 origin memory object - weak property
    #   _action                 action to execute
    #   _context                context for which object was been generated

    # generic attributes
    #   _types                  type wrapper
    #   _id                     uuid
    #   _name                   object's name
    #   _order                  order in parent memory object

    # compiler atributes
    #   _dynamic                dynamic or static object
    #   _optimization_priority  object's optimization priority

    # e2vdom attributes
    #   _types                  all descendant types including object's type
    #   _containers             all containers from _types
    #   _libraries              all descendant types including object's libraries (obsolete)

    # attributes and objects
    #   _attributes             all attributes names
    #   _get_objects            all child object's names

    # stateful attributes
    #   _values                 original attributes values

    def __init__(self, parent):
        # log.write("Initialize %s" % self)
        self._parent = parent
        self._compute_state = STATE_REQUIRE_RECOMPUTE
        self._update_state = STATE_UNMODIFIED
        self._attributes_collection = None
        self._objects_collection = None

    def _get_state(self):
        request = managers.request_manager.current
        return (request.next_state or request.last_state)["#"]

    def _get_attributes(self):
        if self._attributes_collection is None:
            self._attributes_collection = VDOMObjectAttributes(self)
        return self._attributes_collection

    def _get_objects(self):
        if self._objects_collection is None:
            self._objects_collection = VDOMObjectObjects(self)
        return self._objects_collection

    parent = property(lambda self: self._parent)
    state = property(_get_state)

    context = property(lambda self: self._context)

    type = property(lambda self: self._type)
    id = property(lambda self: self._id)
    name = property(lambda self: self._name)
    order = property(lambda self: self._order)

    dynamic = property(lambda self: self._dynamic)
    optimization_priority = property(lambda self: self._optimization_priority)

    attributes = property(_get_attributes)
    objects = property(_get_objects)

    id4code = id_special = property(lambda self: u"o_" + self._id.replace('-', '_'))

    def execute(self, namespace=None):
        action = self._action
        if action:
            log.write("Execute %s" % action)
            action.execute(context=self, namespace=namespace)

    def compute(self):
        # log.write("Compute %s" % self)
        pass

    def render(self, contents=""):
        # log.write("Render %s" % self)
        return contents

    def wysiwyg(self, contents=""):
        # log.write("Wysiwyg %s" % self)
        return contents

    def _instantiate(self, name):
        log.write("Instantiate %s attribute \"%s\" object" % (self, name))

        # obtain context and inmaterial child object
        origin = self._origin
        context = self._context

        # force dynamic to child and recompile
        instance = origin.objects[name].factory(context, dynamic=1)(self)

        # need recompilation due to new dynamic child if it is actual
        with origin.lock:
            if self.__class__ is origin.factory(context, probe=True):
                origin.invalidate(contexts=context, upward=True)

        # assign attribute
        setattr(self, make_object_name(name), instance)

        # switch to dynamic render and wysiwyg
        self.render = self._dynamic_render
        self.wysiwyg = self._dynamic_wysiwyg

        return instance

    def _dynamic_render(self, contents=""):
        log.write("Dynamic render %s" % self)
        chunks = [contents]
        for name in self._objects:
            try:
                instance = getattr(self, make_object_name(name))
            except AttributeError:
                klass = self._origin.objects[name].factory(self._context)
                instance = klass(None)  # no parent for static
            chunks.append(instance.render())
        return self.__class__.__bases__[0].render(self, contents=u"".join(chunks))

    def _dynamic_wysiwyg(self, contents=""):
        log.write("Dynamic wysiwyg %s" % self)
        chunks = [contents]
        for name in self._objects:
            try:
                instance = getattr(self, make_object_name(name))
            except AttributeError:
                klass = self._origin.objects[name].factory(self._context)
                instance = klass(None)  # no parent for static
            chunks.append(instance.wysiwyg())
        return self.__class__.__bases__[0].wysiwyg(self, contents=u"".join(chunks))

    def recompute(self):
        self._compute_state = STATE_RECOMPUTE
        self.compute()
        self._compute_state = STATE_UP_TO_DATE

    def update(self, *names):
        attributes = {}
        for name in names:
            name = unicode(name).lower()
            attributes[name] = getattr(self, name)
        self._origin.attributes.update(attributes)

    def separate_render(self, chunks=None):
        if chunks is None:
            chunks = {}
        if self._update_state is STATE_MODIFIED:
            log.write("Separate render %s" % self)
            chunks[self._id] = self.render()
        else:
            for name in self._objects:
                attribute_name = make_object_name(name)
                if attribute_name in self.__dict__:
                    getattr(self, attribute_name).separate_render(chunks=chunks)
        return chunks

    def write(self, data, action_name=None):
        log.write(u"Write action %s data to client: %d characters" % (action_name, len(data)))
        render_type = managers.request_manager.current.render_type
        if render_type != "e2vdom":
            log.warning("Perform write when render type is \"%s\"" % render_type)
            from utils.tracing import format_thread_trace
            log.warning(format_thread_trace(statements=False, skip=("write", "action"), until="scripting.executable"))
        # else:
        #     from utils.tracing import format_thread_trace
        #     log.debug(format_thread_trace(statements=False, skip=("write", "action"), until="scripting.executable"))

        # log.debug(
        #     u"- - - - - - - - - - - - - - - - - - - -\n"
        #     u"%s\n"
        #     u"- - - - - - - - - - - - - - - - - - - -\n" %
        #     data, module=False)

        # self._compute_state = STATE_AVOID_RECOMPUTE

        managers.request_manager.current.add_client_action(self._id, data)

    def action(self, action_name, arguments=[], source_id=None):
        render_type = managers.request_manager.current.render_type
        if render_type != "e2vdom":
            log.warning("Invoke client action when render type is \"%s\"" % render_type)

        if source_id:
            information = "SRC_ID=\"o_%s\" " % source_id.replace('-', '_')
        else:
            information = ""
        information += "DST_ID=\"%s\" ACT_NAME=\"%s\"" % (self._id.replace('-', '_'), action_name)

        if not isinstance(arguments, (tuple, list)):
            arguments = (arguments,)

        data = (("str", unicode(argument)) if isinstance(argument, basestring) else
            ("obj", unicode(json.dumps(argument)).encode("xml")) for argument in arguments)

        if arguments:
            self.write("<EXECUTE %s>\n%s\n</EXECUTE>" % (information,
                "\n".join("  <PARAM type=\"%s\">%s</PARAM>" % (kind, value.encode("xml")) for kind, value in data)), action_name)
        else:
            self.write("<EXECUTE %s/>" % information, action_name)

    def lookup(self, selector):
        origin = self._origin
        if selector[8:9] == "-":
            if selector == origin.id:
                return origin
            else:
                result = origin.application.objects.catalog.get(selector)
                if result is None:
                    result = origin.primary.objects.catalog.get(selector)
                return result
        else:
            return origin.primary.select(*selector.split("."))

    def _fetch(self):
        log.write("Fetch %s attributes" % self)
        request = managers.request_manager.current
        try:
            self._attributes = (request.next_state or request.last_state)[self._id]
        except KeyError:
            self._attributes = self._values

    def _switch(self):
        log.write("Switch %s attributes" % self)
        request = managers.request_manager.get_request()
        if request.next_state:
            state = request.next_state
            index = state["#"]
        else:
            log.write("Allocate new state")
            request.next_state = state = request.last_state.copy()
            # LOCK SESSION
            session = request.session()
            state["#"] = index = len(session.states)
            session.states.append(state)
            # UNLOCK SESSION
        attributes = state.get(self._id, self._attributes)
        if attributes.get("#", 0) < index:
            state[self._id] = attributes = copy(attributes)
            attributes["#"] = index
        self._attributes = attributes

    def __str__(self):
        return " ".join(filter(None, (
            "object",
            ":".join(filter(None, (self._id, self._name))))))

    def __repr__(self):
        return "<scripting %s at 0x%08X>" % (self, id(self))


VDOM_object = VDOMObject

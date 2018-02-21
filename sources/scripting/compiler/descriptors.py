
from time import time


STATE_UNMODIFIED = "UNMODIFIED"
STATE_MODIFIED = "MODIFIED"

STATE_UP_TO_DATE = "UP TO DATE"
STATE_REQUIRE_RECOMPUTE = "REQUIRE RECOMPUTE"
STATE_RECOMPUTE = "RECOMPUTE"
STATE_AVOID_RECOMPUTE = "AVOID RECOMPUTE"


# exceptions

class AvoidRecomputeError(AttributeError):

    def __init__(self, owner, name):
        super(AttributeError, self).__init__("%r avoid recompute when update %r" % (owner, name))


# name functions

def make_type_class_name(type):
    return "%sType" % type.class_name


def make_attribute_name(name):
    return u"_%s_attribute" % name


def make_object_name(name):
    return u"_%s_object" % name


def make_descriptor_name(name):
    return u"_%s_descriptor" % name


def make_descriptor_class_name(name):
    return "%s_property" % name


# generic descriptors

class Descriptors(dict):

    namespace = {
        "AvoidRecomputeError": AvoidRecomputeError,
        "STATE_UNMODIFIED": STATE_UNMODIFIED,
        "STATE_MODIFIED": STATE_MODIFIED,
        "STATE_UP_TO_DATE": STATE_UP_TO_DATE,
        "STATE_REQUIRE_RECOMPUTE": STATE_REQUIRE_RECOMPUTE,
        "STATE_RECOMPUTE": STATE_RECOMPUTE,
        "STATE_AVOID_RECOMPUTE": STATE_AVOID_RECOMPUTE
    }


class SqueezableDescriptors(Descriptors):

    def squeeze(self, limit=2500):
        # NOTE: possible make something better
        if len(self) > limit:
            self.clear()


# scripting descriptors

class AttributeDescriptors(Descriptors):

    def __missing__(self, name):
        namespace = {}
        source = """
class {class_name}(object):

    __module__ = "scripting"

    def __get__(self, instance, owner):
        if instance._compute_state is STATE_REQUIRE_RECOMPUTE:
            instance.recompute()
        return instance.{attribute_name}

    def __set__(self, instance, value):
        if instance._compute_state is STATE_UP_TO_DATE:
            instance._compute_state = STATE_REQUIRE_RECOMPUTE
        # elif instance._compute_state is STATE_AVOID_RECOMPUTE:
        #     raise AvoidRecomputeError(instance, "{name}")
        if instance._update_state is STATE_UNMODIFIED:
            instance._update_state = STATE_MODIFIED
        instance.{attribute_name} = value

descriptor={class_name}()
        """.format(
            name=name,
            class_name=make_descriptor_class_name(name),
            attribute_name=make_attribute_name(name))

        exec(compile(source, "<scripting attribute descriptor %s>" % name, "exec"),
            self.namespace, namespace)
        return self.setdefault(name, namespace["descriptor"])


class StatefulAttributeDescriptors(Descriptors):

    def __missing__(self, name):
        namespace = {}
        source = """
class {class_name}(object):

    __module__ = "scripting"

    def __get__(self, instance, owner):
        if instance._compute_state is STATE_REQUIRE_RECOMPUTE:
            instance.recompute()
        return instance._attributes["{name}"]

    def __set__(self, instance, value):
        if instance._compute_state is STATE_UP_TO_DATE:
            instance._compute_state = STATE_REQUIRE_RECOMPUTE
        # elif instance._compute_state is STATE_AVOID_RECOMPUTE:
        #     raise AvoidRecomputeError(instance, "{name}")
        if instance._update_state is STATE_UNMODIFIED:
            instance._update_state = STATE_MODIFIED
            instance._switch()
        instance._attributes["{name}"] = value

descriptor={class_name}()
        """.format(
            name=name,
            class_name=make_descriptor_class_name(name))

        exec(compile(source, "<scripting stateful attribute descriptor %s>" % name, "exec"),
            self.namespace, namespace)
        return self.setdefault(name, namespace["descriptor"])


class ObjectDescriptors(SqueezableDescriptors):

    def __missing__(self, name):
        namespace = {}
        source = """
class {class_name}(object):

    __module__ = "scripting"

    def __get__(self, instance, owner):
        return instance.{attribute_name}

descriptor={class_name}()
        """.format(
            name=name,
            class_name=make_descriptor_class_name(name),
            attribute_name=make_object_name(name))

        exec(compile(source, "<scripting object descriptor %s>" % name, "exec"),
            self.namespace, namespace)
        return self.setdefault(name, namespace["descriptor"])


class GhostObjectDescriptors(SqueezableDescriptors):

    def __missing__(self, name):
        namespace = {}
        source = """
class {class_name}(object):

    __module__ = "scripting"

    def __get__(self, instance, owner):
        try:
            return instance.{attribute_name}
        except AttributeError:
            return instance._instantiate("{name}")

descriptor={class_name}()
        """.format(
            name=name,
            class_name=make_descriptor_class_name(name),
            attribute_name=make_object_name(name))

        exec(compile(source, "<scripting ghost object descriptor %s>" % name, "exec"),
            self.namespace, namespace)
        return self.setdefault(name, namespace["descriptor"])


# scripting type

def create_type_object(type):
    namespace = {
        "_id": type.id,
        "_name": type.name,
        "_version": type.version
    }

    source = """
class {class_name}(object):

    __module__ = "scripting"

    _id = _id
    _name = _name
    _version = _version

    id = property(lambda self: self.__class__._id)
    name = property(lambda self: self.__class__._name)
    version = property(lambda self: self.__class__._version)
    class_name = property(lambda self: "{name}")

object={class_name}()
    """.format(
        name=type.class_name,
        class_name=make_type_class_name(type))

    exec(compile(source, "<scripting type %s>" % type, "exec"), namespace)
    return namespace["object"]

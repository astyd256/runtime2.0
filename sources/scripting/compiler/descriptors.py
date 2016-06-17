

STATE_UNMODIFIED = "UNMODIFIED"
STATE_MODIFIED = "MODIFIED"

STATE_UP_TO_DATE = "UP TO DATE"
STATE_REQUIRE_RECOMPUTE = "REQUIRE RECOMPUTE"
STATE_RECOMPUTE = "RECOMPUTE"
STATE_AVOID_RECOMPUTE = "AVOID RECOMPUTE"


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
    return "ScriptingObject%sDescriptor" % "".join(part.capitalize() for part in name.split("_"))


# exceptions

class AvoidRecomputeError(AttributeError):

    def __init__(self, owner, name):
        super(AttributeError, self).__init__("%r avoid recompute when update %r" % (owner, name))


# scripting type creator

def create_type_object(type):
    namespace = {
        "_id": type.id,
        "_name": type.name,
        "_version": type.version
    }

    class_name = make_type_class_name(type)

    source = """class {class_name}(object):

    _id = _id
    _name = _name
    _version = _version

    id = property(lambda self: self.__class__._id)
    name = property(lambda self: self.__class__._name)
    version = property(lambda self: self.__class__._version)

object={class_name}()""".format(
        name=type.class_name,
        class_name=class_name)

    exec(compile(source, "<scripting type %s>" % type, "exec"), namespace)
    return namespace["object"]


# descriptor creators

def create_attribute_descriptor(name):
    namespace = {
        "AvoidRecomputeError": AvoidRecomputeError,
        "STATE_UNMODIFIED": STATE_UNMODIFIED,
        "STATE_MODIFIED": STATE_MODIFIED,
        "STATE_UP_TO_DATE": STATE_UP_TO_DATE,
        "STATE_REQUIRE_RECOMPUTE": STATE_REQUIRE_RECOMPUTE,
        "STATE_RECOMPUTE": STATE_RECOMPUTE,
        "STATE_AVOID_RECOMPUTE": STATE_AVOID_RECOMPUTE
    }

    class_name = make_descriptor_class_name(name)
    attribute_name = make_attribute_name(name)

    source = """class {class_name}(object):

    def __get__(self, instance, owner):
        if instance._compute_state is STATE_REQUIRE_RECOMPUTE:
            instance.recompute()
        return instance.{attribute_name}

    def __set__(self, instance, value):
        if instance._compute_state is STATE_UP_TO_DATE:
            instance._compute_state = STATE_REQUIRE_RECOMPUTE
        elif instance._compute_state is STATE_AVOID_RECOMPUTE:
            raise AvoidRecomputeError(instance, "{name}")
        if instance._update_state is STATE_UNMODIFIED:
            instance._update_state = STATE_MODIFIED
        instance.{attribute_name} = value

descriptor={class_name}()""".format(
        name=name,
        class_name=class_name,
        attribute_name=attribute_name)

    exec(compile(source, "<scripting attribute descriptor %s>" % name, "exec"), namespace)
    return namespace["descriptor"]


def create_stateful_attribute_descriptor(name):
    namespace = {
        "AvoidRecomputeError": AvoidRecomputeError,
        "STATE_UNMODIFIED": STATE_UNMODIFIED,
        "STATE_MODIFIED": STATE_MODIFIED,
        "STATE_UP_TO_DATE": STATE_UP_TO_DATE,
        "STATE_REQUIRE_RECOMPUTE": STATE_REQUIRE_RECOMPUTE,
        "STATE_RECOMPUTE": STATE_RECOMPUTE,
        "STATE_AVOID_RECOMPUTE": STATE_AVOID_RECOMPUTE
    }

    class_name = make_descriptor_class_name(name)

    source = """class {class_name}(object):

    def __get__(self, instance, owner):
        if instance._compute_state is STATE_REQUIRE_RECOMPUTE:
            instance.recompute()
        return instance._attributes["{name}"]

    def __set__(self, instance, value):
        if instance._compute_state is STATE_UP_TO_DATE:
            instance._compute_state = STATE_REQUIRE_RECOMPUTE
        elif instance._compute_state is STATE_AVOID_RECOMPUTE:
            raise AvoidRecomputeError(instance, "{name}")
        if instance._update_state is STATE_UNMODIFIED:
            instance._update_state = STATE_MODIFIED
            instance._switch()
        instance._attributes["{name}"] = value

descriptor={class_name}()""".format(
        name=name,
        class_name=class_name)

    exec(compile(source, "<scripting stateful attribute descriptor %s>" % name, "exec"), namespace)
    return namespace["descriptor"]


def create_object_descriptor(name):
    namespace = {}

    class_name = make_descriptor_class_name(name)
    attribute_name = make_object_name(name)

    source = """class {class_name}(object):

    def __get__(self, instance, owner):
        return instance.{attribute_name}

descriptor={class_name}()""".format(
        name=name,
        class_name=class_name,
        attribute_name=attribute_name)

    exec(compile(source, "<scripting object descriptor %s>" % name, "exec"), namespace)
    return namespace["descriptor"]


def create_ghost_object_descriptor(name):
    namespace = {}

    class_name = make_descriptor_class_name(name)
    attribute_name = make_object_name(name)

    source = """
class {class_name}(object):

    def __get__(self, instance, owner):
        try:
            return instance.{attribute_name}
        except AttributeError:
            return instance._instantiate("{name}")

descriptor={class_name}()""".format(
        name=name,
        class_name=class_name,
        attribute_name=attribute_name)

    exec(compile(source, "<scripting ghost object descriptor %s>" % name, "exec"), namespace)
    return namespace["descriptor"]

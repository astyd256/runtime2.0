
import re
import managers

from logs import log
from utils.properties import weak

from .profile import CompilationProfile
from .descriptors import make_attribute_name, make_object_name, make_descriptor_name, \
    create_attribute_descriptor, create_stateful_attribute_descriptor, \
    create_object_descriptor, create_ghost_object_descriptor


DEFAULT_MODULE_NAME = "scripting.classes"
UUID_REGEX = re.compile(r"^([A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})$", re.IGNORECASE)
# MAXIMAL_LINE_LENGTH = 139


class Compiler(object):

    def compile(self, origin, context, dynamic=None, mapping=None):
        # origin: type, id, name, order, stateful, hierarchy
        #         attributes, objects, actions.get(context)
        #         factory(context)
        log.write("Compile %s in %s context%s" % (origin, context, (" as dynamic" if dynamic else "")))

        # prepare compilation profile and execute on_compile
        profile = CompilationProfile(origin, context, dynamic=dynamic, mapping=mapping)
        with profile:
            managers.dispatcher.dispatch_handler(origin, "on_compile", profile)

        # e2vdom atributes
        types = {origin.type}

        # check necessity to execute all such actions along object hierarchy
        chaining = not UUID_REGEX.match(context)

        # store all object's declared identifiers
        instance_namespace = {name for name in dir(origin.type.klass) if not name.startswith("_")}

        # declare source lists
        source, initialize, execute, render, wysiwyg = [], [], [], [], []
        render_contents, wysiwyg_contents = [], []

        # prepare class namespace
        module_namespace = {}
        class_namespace = {
            "__module__": DEFAULT_MODULE_NAME,

            # internal attributes
            # "_origin": origin, - now weak and created later
            "_action": profile.action,
            "_context": context,

            # generic attributes
            "_type": origin.type.factory(context),
            "_id": origin.id,
            "_name": origin.name,
            "_order": origin.order,

            # compiler atributes
            "_dynamic": profile.dynamic,
            "_optimization_priority": profile.optimization_priority,

            # e2vdom attributes
            "_types": types,

            # attributes and objects
            "_attributes": tuple(name for name in origin.attributes),
            "_objects": tuple(entry.origin.name for entry in profile.entries),
            "_ghosts": tuple(entry.origin.name for entry in profile.entries if not entry.dynamic)
        }

        if profile.stateful:
            # enable stateful behaviour
            class_namespace["_values"] = {name: value for name, value in origin.attributes.iteritems()}
            initialize.append(u"\tself._fetch()\n")

            # add stateful attributes descriptors
            for name in origin.attributes:
                descriptor = create_stateful_attribute_descriptor(name)
                class_namespace[make_descriptor_name(name)] = descriptor
                if name not in instance_namespace:
                    class_namespace[name] = descriptor
                    instance_namespace.add(name)
        else:
            # add usual attributes and descriptors
            for name, value in origin.attributes.iteritems():
                class_namespace[make_attribute_name(name)] = value
                descriptor = create_attribute_descriptor(name)
                class_namespace[make_descriptor_name(name)] = descriptor
                if name not in instance_namespace:
                    class_namespace[name] = descriptor
                    instance_namespace.add(name)

        # go through objects
        for entry in profile.entries:
            # cache variables
            entry_class = entry.klass
            entry_origin_name = entry.origin.name

            # gather e2vdom atributes
            types |= entry_class._types

            if entry.dynamic:
                # cache variable
                entry_class_name = entry_class.__name__

                # generate name
                object_name = make_object_name(entry_origin_name)

                # add to namespace and insert declaration
                module_namespace[entry_class_name] = entry_class
                initialize.append(u"\tself.%s = %s(self)\n" % (object_name, entry_class_name))

                # add descriptor if identifier already not in use
                if entry_origin_name not in instance_namespace:
                    class_namespace[entry_origin_name] = create_object_descriptor(entry_origin_name)
                    instance_namespace.add(entry_origin_name)

                # add optional handlers
                for where, name in (
                        (initialize, "on_initialize"),
                        (execute, "on_execute"),
                        (render, "on_render"),
                        (wysiwyg, "on_wysiwyg")):
                    handler = getattr(entry, name)
                    if handler:
                        handler_name = u"object_%s_%s" % (entry_origin_name, name)
                        class_namespace[handler_name] = handler
                        where.append(u"\tself.%s(self.%s)\n" % (handler_name, object_name))

                # add action execution in case of chaining
                if chaining:
                    execute.append(u"\tself.%s.execute(namespace)\n" % object_name)

                # add render and wysiwyg calls
                render_contents.append(u", self.%s.render()" % object_name)
                wysiwyg_contents.append(u", self.%s.wysiwyg()" % object_name)
            else:
                # add ghost descriptor if identifier already not in use
                if entry_origin_name not in instance_namespace:
                    class_namespace[entry_origin_name] = create_ghost_object_descriptor(entry_origin_name)
                    instance_namespace.add(entry_origin_name)

                log.write("Prerender \"%s\" for %s" % (entry_origin_name, origin))

                # TODO: there are possible problems with deleting this child or origin object
                #       during execute, render or wysiwyg execution in overrided type's methods

                # instantiate
                instance = entry_class(None)  # no parent here also skip execute due static

                # add render and wysiwyg contents
                render_contents.append(u", %r" % instance.render())
                wysiwyg_contents.append(u", %r" % instance.wysiwyg())

        # autogenerate position attribute for some reason
        # TODO: check it later
        if u"top" in origin.attributes and "left" in origin.attributes:
            class_namespace["position"] = "absolute"

        # append initialize sources
        if initialize:
            source.append(u"def __init__(self, parent):\n")
            source.append(u"\tsuper(%s, self).__init__(parent)\n" % profile.class_name)
            source.extend(initialize)

        # append execute sources
        if execute:
            source.append(u"def execute(self, namespace=None):\n")
            source.extend(execute)
            source.append(u"\tsuper(%s, self).execute(namespace)\n" % profile.class_name)

        # append render sources
        if render or render_contents:
            source.append(u"def render(self, contents=\"\"):\n")
            if render:
                source.extend(render)
            source.append(u"\treturn super(%s, self).render(contents=u\"\".join((contents" % profile.class_name)
            if render_contents:
                source.extend(render_contents)
            source.append(u")))\n")

        # append wysiwyg sources
        if wysiwyg or wysiwyg_contents:
            source.append(u"def wysiwyg(self, contents=\"\"):\n")
            if wysiwyg:
                source.extend(wysiwyg)
            source.append(u"\treturn super(%s, self).wysiwyg(contents=u\"\".join((contents" % profile.class_name)
            if wysiwyg_contents:
                source.extend(wysiwyg_contents)
            source.append(u")))\n")

        # create class with weak origin
        klass = weak(_origin=origin)(type(str(profile.class_name), (origin.type.klass,), class_namespace))

        # compile methods
        if source:
            # log.write("Compose %s in %s context" % (origin, context))
            # from utils.auxiliary import fit
            # clean_source = "\n".join(fit(line, MAXIMAL_LINE_LENGTH) for line in "".join(source).splitlines())
            # log.debug(
            #     u"- - - - - - - - - - - - - - - - - - - -\n"
            #     u"%s\n"
            #     u"- - - - - - - - - - - - - - - - - - - -" %
            #     clean_source.replace("\t", "    "), module=False)

            # compile and execute
            code = compile(u"".join(source), u"<class %s>" % origin.id, u"exec")
            module_namespace[profile.class_name] = klass
            exec(code, module_namespace)

            # assign methods
            for name in ("__init__", "execute", "render", "wysiwyg"):
                method = module_namespace.get(name)
                if method:
                    # log.write("Override \"%s\" for %s" % (name, origin))
                    setattr(klass, name, method)

        return klass


VDOM_compiler = Compiler

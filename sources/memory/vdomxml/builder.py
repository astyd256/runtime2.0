
import managers
from utils.structure import Structure
from utils.parsing import native, UnexpectedAttributeValueError, MissingAttributeError


def vdomxml_builder(parser, application):
    # TODO: think much more about type indexing
    catalog = {type.name: type for type in managers.memory.types.itervalues()}

    def create_object(objects, name, attributes):
        try:
            object_type = catalog[name.lower()]
        except KeyError:
            raise UnexpectedAttributeValueError("Unknown type: %s" % name)

        try:
            object_name = attributes.pop("name")
        except KeyError:
            raise MissingAttributeError("Require name")

        object = objects.new(object_type, name=object_name, virtual=True)
        object.attributes.update(attributes)
        attributes.clear()
        return object

    # <element>
    @native
    def container(name, attributes):
        context = Structure(parent=None)
        # <element>
        @native
        def element(name, attributes):
            parent = context.parent
            context.parent = create_object(parent.objects, name, attributes)
            yield element
            context.parent = parent
        # </element>
        context.parent = create_object(application.objects, name, attributes)
        yield element
        parser.accept(context.parent)
    # </element>

    return container

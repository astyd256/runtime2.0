
from uuid import uuid4
import managers
from utils.structure import Structure
from utils.parsing import VALUE, native, UnexpectedAttributeValueError, MissingAttributeError


def vdomxml_builder(parser, origin):
    objects = []

    def create_object(parent_objects, name, attributes):
        object_type = managers.memory.types.search(name)
        if object_type is None:
            raise UnexpectedAttributeValueError("Unknown type: %s" % name)

        try:
            object_name = attributes.pop("name")
        except KeyError:
            raise MissingAttributeError("Require name")

        object = parent_objects.new_sketch(object_type, virtual=True)
        object.id = str(uuid4())
        object.name = object_name

        object.attributes.update(attributes)
        attributes.clear()

        objects.append(object)
        return object

    # <element>
    @native
    def container(name, attributes):
        context = Structure(parent=None)
        # <element>
        @native
        def element(name, attributes):
            if name == "attribute":
                key = attributes.pop("name")
                value = yield VALUE
                context.parent.attributes[key] = value
            else:
                parent = context.parent
                context.parent = create_object(parent.objects, name, attributes)
                yield element
                context.parent = parent
        # </element>
        context.parent = create_object(origin.objects, name, attributes)

        yield element
        for object in objects:
            ~object

        parser.accept(context.parent)
    # </element>

    return container

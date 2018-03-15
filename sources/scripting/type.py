
class VDOMType(object):

    # attributes that initialized by the compiler at runtime

    #   _id                     uuid
    #   _name                   type's name
    #   _version                version
    #   _class_name             class name

    id = property(lambda self: self._id)
    name = property(lambda self: self._name)
    version = property(lambda self: self._version)
    class_name = property(lambda self: self._class_name)

    def __str__(self):
        return " ".join(filter(None, (
            "type",
            ":".join(filter(None, (self._id, self._name))))))

    def __repr__(self):
        return "<scripting %s at 0x%08X>" % (self, id(self))

    def __describe__(self):
        return "scripting " + str(self)


class MemoryBase(object):

    def __invert__(self):
        raise NotImplementedError

    def __repr__(self):
        return "<memory %s at 0x%08X>" % (self, id(self))

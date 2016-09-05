
class Storage(object):

    def locate(self, entity):
        raise NotImplementedError

    def exists(self, entity):
        raise NotImplementedError

    def read(self, entity):
        raise NotImplementedError

    def write(self, entity, value):
        raise NotImplementedError

    def delete(self, entity):
        raise NotImplementedError

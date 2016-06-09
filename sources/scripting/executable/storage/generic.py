
from utils.properties import lazy, roproperty


class CodeStorage(object):

    @lazy
    def _location(self):
        raise NotImplementedError

    location = roproperty("_location")

    def _exists(self, extension):
        raise NotImplementedError

    def _read(self, extension):
        raise NotImplementedError

    def _write(self, extension, value):
        raise NotImplementedError

    def _delete(self, extension):
        raise NotImplementedError

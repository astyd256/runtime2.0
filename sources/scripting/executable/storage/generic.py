
class CodeStorage(object):

    def _exists(self, extension):
        raise NotImplementedError

    def _read(self, extension):
        raise NotImplementedError

    def _write(self, extension, value):
        raise NotImplementedError

    def _delete(self, extension):
        raise NotImplementedError

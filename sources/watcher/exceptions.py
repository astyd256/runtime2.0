

class WatcherError(Exception):
    pass


class WatcherManualException(Exception):

    pass


class OptionError(WatcherError):

    def __init__(self, message=None, name=None):
        if not message:
            if name:
                message = "Incorrect option \"%s\"" % name
            else:
                message = "Incorrect option"
        super(OptionError, self).__init__(message)


class NoSnapshotError(WatcherError):

    def __init__(self, message="No snapshot available"):
        super(NoSnapshotError, self).__init__(message)

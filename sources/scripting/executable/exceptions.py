
class SourceSyntaxError(Exception):

    def __init__(self, message, lineno=None):
        super(Exception, self).__init__(message)
        self.lineno = lineno


class ExecutionTimeoutError(Exception):
    pass

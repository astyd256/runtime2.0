

class ExecutableException(Exception):
    pass


class SourceSyntaxError(ExecutableException):

    def __init__(self, message, lineno=None):
        super(ExecutableException, self).__init__(message)
        self.lineno = lineno

    def __str__(self):
        result = super(ExecutableException, self).__str__()
        if self.lineno:
            result += " in line %d" % self.lineno
        return result


class CompilationError(ExecutableException):

    def __init__(self, message, source, cause=None):
        super(ExecutableException, self).__init__(message)
        self.source = source
        self.cause = cause


class RequirePrecompileError(ExecutableException):

    def __init__(self, message, executable):
        super(ExecutableException, self).__init__(message)
        self.executable = executable

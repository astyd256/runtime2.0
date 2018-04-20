
import sys
import os
import settings


class OutputBuffer(object):

    def __init__(self):
        self._file = None
        self._lines = None

    def __enter__(self):
        if self._file:
            raise Exception("Unable to re-enter")
        self._echo = os.fdopen(os.dup(sys.stdout.fileno()), "w")
        self._filename = os.path.join(settings.TEMPORARY_LOCATION, "setup.log")
        self._file = open(self._filename, "w+")
        self._stdout_duplicate = os.dup(sys.stdout.fileno())
        self._stderr_duplicate = os.dup(sys.stderr.fileno())
        os.dup2(self._file.fileno(), sys.stdout.fileno())
        os.dup2(self._file.fileno(), sys.stderr.fileno())
        return self

    def __exit__(self, extype, exvalue, extraceback):
        os.dup2(self._stdout_duplicate, sys.stdout.fileno())
        os.dup2(self._stderr_duplicate, sys.stderr.fileno())
        self._file.seek(0)
        self._lines = self._file.read().splitlines()
        self._file.close()
        self._file = None
        os.remove(self._filename)
        self._echo.close()

    lines = property(lambda self: self._lines)

    def echo(self, message):
        if self._file:
            self._echo.write(message + "\n")
        else:
            print message

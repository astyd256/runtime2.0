
from threading import current_thread, Lock
import settings
from logs import console, log


LOGGING = None


class GenericOutput(object):

    def __init__(self, output):
        self._output = output
        self._buffer = []
        self._lock = Lock()

    def _write(self, message):
        raise NotImplementedError

    def write(self, message):
        with self._lock:
            try:
                most, last = message.rsplit("\n", 1)
            except ValueError:
                self._buffer.append(message)
            else:
                self._buffer.append(most)
                self._write("".join(self._buffer))
                self._buffer = [last]

    def flush(self):
        message = "".join(self._buffer)
        if message:
            self._write(message)
            self._buffer = []


class SeparateOutput(object):

    def __init__(self, output):
        self._output = output
        self._buffer = {}
        self._lock = Lock()

    def _write(self, message):
        raise NotImplementedError

    def write(self, message):
        thread = current_thread()

        # HACK: sometimes print output unexpected space
        if message == " " and thread not in self._buffer:
            return

        try:
            most, last = message.rsplit("\n", 1)
            most += "\n"
        except ValueError:
            try:
                self._buffer[thread].append(message)
            except KeyError:
                self._buffer[thread] = [message]
        else:
            try:
                buffer = self._buffer[thread]
            except KeyError:
                pass
            else:
                buffer.append(most)
                most = "".join(buffer)
            with self._lock:
                self._write(most)
            self._buffer[thread] = [last]

    def flush(self):
        thread = current_thread()
        try:
            rest = "".join(self._buffer[thread])
        except KeyError:
            pass
        else:
            if rest:
                with self._lock:
                    self._write(rest)
                self._buffer[thread] = []


class Output(SeparateOutput):

    def _write(self, message):
        if settings.LOGGING_OUTPUT:
            log.write(message)


class ErrorOutput(SeparateOutput):

    def _write(self, message):
        if settings.LOGGING_OUTPUT:
            log.error(message)

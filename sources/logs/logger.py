
import weakref
import socket
from collections import deque
from threading import Lock
import settings
from logs import log
from utils.threads import SmartDaemon
from . import actions
from .packer import create_packer
from .stream import LogSocketStream


COUNTDOWN = 3.0
RECONNECT_TIMEOUT = 5


class Logger(SmartDaemon):

    name = "Logger"

    def __init__(self, address=settings.LOGGING_ADDRESS, port=settings.LOGGING_PORT):

        def condition():
            with self._lock:
                return not self._queue

        super(Logger, self).__init__(name=Logger.name,
            condition=condition, countdown=COUNTDOWN, latter=True)
        self._address = address
        self._port = port
        self._available = deque(range(256))
        self._mapping = {}
        self._counters = {}
        self._actual = {}
        self._queue = deque()
        self._lock = Lock()
        self._stream = None

    def ascribe(self, sublog):

        # return fake if no logging
        if not settings.LOGGING:

            def fake(*arguments):
                pass

            return fake

        # prepare packer and perform assume
        name, packer = sublog.name, sublog.packer
        with self._lock:
            try:
                id = self._mapping[name]
                self._counters[id] += 1
            except KeyError:
                self._mapping[name] = id = self._available.popleft()
                self._counters[id] = 1
                self._queue.append((actions.ASSUME, id, name))

        def enqueue(*values):
            with self._lock:
                self._queue.append((actions.WRITE, id, packer, values))

        def cleanup(nothing):
            proxy  # prevent to unlink proxy
            with self._lock:
                self._counters[id] -= 1
                if self._counters[id] == 0:
                    self._queue.append((actions.REVOKE, id))
                    del self._mapping[name]
                    del self._counters[id]
                    self._available.appendleft(id)

        # return enqueue
        proxy = weakref.proxy(enqueue, cleanup)
        return enqueue

    def prepare(self):
        log.write("Start " + self.name)

    def cleanup(self):
        log.write("Stop " + self.name)
        self._stream = None

    _assume_request = create_packer("BBS")
    _revoke_request = create_packer("BB")
    _write_request = create_packer("BBL")

    def work(self):
        if not settings.LOGGING:
            return

        # obtain entry(ies)
        with self._lock:
            try:
                entry = self._queue.popleft()
            except IndexError:
                return

            # consume as much write actions as possible
            if entry[0] == actions.WRITE:
                entries, id = [entry], entry[1]
                while self._queue:
                    next_entry = self._queue[0]
                    if next_entry[0] != actions.WRITE or next_entry[1] != id:
                        break
                    entries.append(self._queue.popleft())

        # def restore():
        #     with self._lock:
        #         if entry[0] in (actions.ASSUME, actions.REVOKE):
        #             self._queue.appendleft(entry)
        #         else:
        #             for entry in reversed(entries):
        #                 self._queue.appendleft(entry)

        # send entry(ies)
        try:
            if self._stream is None:

                # (re)connect to the server
                while True:
                    log.write("Connect to %s:%d" % (self._address, self._port))
                    stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    stream_socket.settimeout(RECONNECT_TIMEOUT) # self.quantum
                    try:
                        stream_socket.connect((self._address, self._port))
                        break
                    except socket.timeout:
                        if not self.running:
                            return
                    except socket.error as error:
                        log.error(error.strerror or str(error))

                # create stream
                self._stream = LogSocketStream(self, stream_socket)
                with self._lock:
                    for id, name in self._actual.iteritems():
                        self._queue.appendleft((actions.ASSUME, id, name))

            # send entry(ies) to the server
            try:
                if entry[0] == actions.ASSUME:
                    self._assume_request.pack_into(self._stream, actions.ASSUME, entry[1], entry[2])
                    with self._lock:
                        self._actual[entry[1]] = entry[2]
                elif entry[0] == actions.REVOKE:
                    self._revoke_request.pack_into(self._stream, actions.REVOKE, entry[1])
                    with self._lock:
                        del self._actual[entry[1]]
                else:
                    self._write_request.pack_into(self._stream, actions.WRITE, entry[1], len(entries))
                    for index, entry in enumerate(entries):
                        entry[2].pack_into(self._stream, *entry[3])
                return 0
            except socket.error as error:
                log.error(error.strerror or error.message)
                self._stream = None
        except:
            with self._lock:
                if entry[0] == actions.WRITE:
                    self._queue.extendleft(entries)
                else:
                    self._queue.appendleft(entry)
            raise

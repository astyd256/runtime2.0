
import traceback
import socket
import select

import settings

from logs import log
from utils.threads import SmartThread
from utils.parsing import Parser, ParsingException

from .registry import modules
from .builder import builder
from .session import WatcherSession


class Watcher(SmartThread):

    name = "Watcher"

    def __init__(self):
        super(Watcher, self).__init__(name=Watcher.name)

        if not settings.WATCHER:
            self.stop()
            return

        self._address = settings.WATCHER_ADDRESS
        self._port = settings.WATCHER_PORT
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self._address, self._port))
        self._session_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._session_socket.bind((self._address, self._port))
        self._session_socket.listen(3)

    def prepare(self):
        log.write("Start " + self.name)

    def cleanup(self):
        log.write("Stop " + self.name)
        self._socket = None

    def main(self):
        parser = Parser(builder=builder, result=[])
        parser.cache = True
        log.write("Listen on %s:%d" % (self._address or "*", self._port))
        while self.running:
            try:
                reading, writing, erratic = select.select((self._socket, self._session_socket), (), (), self.quantum)
            except select.error:
                log.error("Unable to check state")
            else:
                if self._socket in reading:
                    try:
                        message, address = self._socket.recvfrom(512)
                    except socket.error:
                        log.error("Unable to receive request")
                        continue
                    log.write("Receive request from %s" % address[0])
                    try:
                        parser.parse(chunk="<session>")
                        parser.parse(chunk=message)
                        parser.parse("</session>")
                    except ParsingException as error:
                        try:
                            self._socket.sendto("<reply><error>Incorrect request: %s</error></reply>" % error, address)
                        except socket.error:
                            log.error("Unable to send response")
                    else:
                        for name, options in parser.result:
                            try:
                                handler = modules[name]
                            except KeyError:
                                response = "<reply><error>Incorrect request</error></reply>"
                            else:
                                try:
                                    log.write("Invoke \"%s\" for %s" % (name, address[0]))
                                    response = "".join(handler(options))
                                except:
                                    log.error("Unable to execute action")
                                    traceback.print_exc()
                                    response = "<reply><error>Internal error</error></reply>"
                            if not response:
                                response = "<reply><error>No reply</error></reply>"
                            try:
                                self._socket.sendto(response, address)
                            except socket.error:
                                log.error("Unable to send response")
                    parser.reset(result=[])
                if self._session_socket in reading:
                    try:
                        session_socket, address = self._session_socket.accept()
                    except socket.error:
                        log.error("Unable to accept connection")
                    log.write("Start session with %s" % session_socket.getpeername()[0])
                    WatcherSession(session_socket, address).start()


VDOM_watcher = Watcher

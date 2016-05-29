
import traceback
import socket
import select

from logs import log
from utils.threads import SmartThread
from utils.parsing import Parser, ParsingException

from .builder import builder
from .registry import modules


class WatcherSession(SmartThread):

    name = "Watcher Session"

    def __init__(self, socket, address):
        super(WatcherSession, self).__init__(name=self.name)
        # name=" ".join((self.name_template, socket.getpeername()[0]))
        self._socket = socket
        self._address = address

    def prepare(self):
        log.write("Start " + self.name)

    def cleanup(self):
        log.write("Stop " + self.name)
        self._socket = None

    def main(self):
        parser = Parser(builder=builder, result=[])
        parser.cache = True
        parser.parse(chunk="<session>")
        while self.running:
            try:
                reading, writing, erratic = select.select((self._socket,), (), (), self.quantum)
            except select.error:
                log.error("Unable to check session state")
            else:
                if reading:
                    try:
                        message = self._socket.recv(4096)
                    except socket.error:
                        log.error("Unable to receive request")
                        break
                    if not message:
                        break
                    try:
                        parser.parse(chunk=message)
                    except ParsingException:
                        log.error("Unable to parse request")
                        try:
                            self._socket.send("<reply><error>Incorrect request</error></reply>")
                        except socket.error:
                            log.error("Unable to send response")
                        break
                    for name, options in parser.result:
                        try:
                            handler = modules[name]
                        except KeyError:
                            log.error("Unable to find action")
                            response = "<reply><error>Incorrect request</error></reply>"
                        else:
                            try:
                                log.write("Invoke \"%s\" for %s" % (name, self._address[0]))
                                response = "".join(handler(options))
                            except:
                                log.error("Unable to execute action")
                                traceback.print_exc()
                                response = "<reply><error>Internal error</error></reply>"
                        if not response:
                            response = "<reply><error>No reply</error></reply>"
                        try:
                            self._socket.send(response)
                        except socket.error:
                            log.error("Unable to send response")
                            break
                    del parser.result[:]
        self._socket.close()

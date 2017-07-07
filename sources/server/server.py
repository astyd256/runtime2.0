
from utils.threads import SmartServer
from utils.profiling import profiler
from watcher import Watcher
from web import VDOM_web_server_thread


class Server(SmartServer):

    def prepare(self):

        self._watcher = Watcher()
        self._watcher.start()

        self._web_server = VDOM_web_server_thread()
        self._web_server.start()

    def work(self):
        profiler.autosave()


VDOM_server = Server


from utils.threads import SmartServer
from watcher import Watcher
from web import VDOM_web_server_thread


class Server(SmartServer):

    def prepare(self):

        self._watcher = Watcher()
        self._watcher.start()

        self._web_server = VDOM_web_server_thread()
        self._web_server.start()

    # def work(self):
    #     data = raw_input()
    #     try:
    #         exec(data, self._namespace)
    #     except Exception as error:
    #         console.error(error)


VDOM_server = Server

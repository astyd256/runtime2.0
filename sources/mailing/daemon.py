
import sys
from utils.threads import VDOM_daemon


class VDOM_mailer(VDOM_daemon):

    name = "Mailer"

    def __init__(self, manager):
        VDOM_daemon.__init__(self, name=VDOM_mailer.name)
        self.__manager = manager

    def prepare(self):
        sys.stderr.write("Start %s\n" % self.name)

    def cleanup(self):
        sys.stderr.write("Stop %s\n" % self.name)
        self.__manager.work()

    def work(self):
        self.__manager.work()

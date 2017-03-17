
import managers
from utils.threads import SmartThread


class Task(SmartThread):

    def __init__(self, *arguments, **keywords):
        self._target = keywords.pop("target", None)
        if keywords.pop("daemon", None):
            self.daemon = True
        super(Task, self).__init__(*arguments, **keywords)

    def start(self):
        self.__application = managers.engine.application
        super(Task, self).start()

    def main(self):
        if self._target:
            self._target()

    def run(self):
        managers.engine.select(self.__application)
        del self.__application
        super(Task, self).run()

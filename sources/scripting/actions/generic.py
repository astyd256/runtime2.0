
import settings
from engine import VDOM_sandbox


class VDOM_generic_action(object):

    def __init__(self, action):
        self._action = action
        self._code = None

    def _compile(self, package):
        raise NotImplementedError

    def _invoke(self, code, object, namespace):
        raise NotImplementedError

    def execute(self, object, namespace):
        application = self._action.owner.application
        if not self._code:
            self._code = self._compile(application.id)
        VDOM_sandbox(self._invoke).execute(settings.SCRIPT_TIMEOUT, arguments=(self._code, object, namespace))

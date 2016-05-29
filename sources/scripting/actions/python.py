
from __future__ import absolute_import
from logs import server_log
from ..wrappers import server, application, session, log, request, response, obsolete_request
from .generic import VDOM_generic_action


class VDOM_python_action(VDOM_generic_action):

    signature = "python"

    def __init__(self, action):
        VDOM_generic_action.__init__(self, action)
        self._package = None

    def _compile(self, package):
        self._package = package
        server_log.debug(
            "- - - - - - - - - - - - - - - - - - - -\n%s\n- - - - - - - - - - - - - - - - - - - -" % self._action.source_code,
            module=False)
        return compile(self._action.source_code, "Action %s %s" % (self._action.id, self._action.name), u"exec")

    def _invoke(self, code, object, namespace):
        __import__(self._package)
        namespace["__package__"] = self._package
        namespace["self"] = object
        namespace["server"] = server
        namespace["request"] = request
        namespace["response"] = response
        namespace["session"] = session
        namespace["application"] = application
        namespace["log"] = log
        namespace["obsolete_request"] = obsolete_request
        exec code in namespace


from __future__ import absolute_import
from vscript.engine import vcompile, vexecute
from .generic import VDOM_generic_action


class VDOM_vscript_action(VDOM_generic_action):

    signature = "vscript"

    def __init__(self, action):
        VDOM_generic_action.__init__(self, action)
        self._vscript_source = None

    def _compile(self, package):
        code, self._vscript_source = vcompile(
            self._action.source_code,
            filename="<action %s:%s>" % (self._action.id, self._action.name),
            package=package)
        return code

    def _invoke(self, code, object, namespace):
        vexecute(code, self._vscript_source, object, namespace)


from utils.exception import VDOM_exception
from .python import VDOM_python_action
from .vscript import VDOM_vscript_action


classes = {
    VDOM_python_action.signature: VDOM_python_action,
    VDOM_vscript_action.signature: VDOM_vscript_action}


def select(language):
    try:
        return classes[language]
    except KeyError:
        raise VDOM_exception("Unknown action language")

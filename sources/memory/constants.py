
PYTHON_LANGUAGE = "python"
VSCRIPT_LANGUAGE = "vscript"

PYTHON_EXTENSION = ".py"
VSCRIPT_EXTENSION = ".vs"
BYTECODE_EXTENSION = COMPILED_EXTENSION = ".bin"
SYMBOLS_EXTENSION = ".sym"

NON_CONTAINER = 1
CONTAINER = 2
TOP_CONTAINER = 3

DEFAULT_APPLICATION_NAME = "Application"
DEFAULT_SCRIPTING_LANGUAGE = VSCRIPT_LANGUAGE
DEFAULT_LANGUAGE = u"en-US"

COMPUTE_CONTEXT = RENDER_CONTEXT = SCRIPT_CONTEXT = "onload" # "onrender"
WYSIWYG_CONTEXT = "onwysiwyg"

APPLICATION_START_CONTEXT = "applicationonstart"
APPLICATION_FINISH_CONTEXT = "applicationonfinish"  # not available
APPLICATION_UNINSTALL_CONTEXT = "applicationonuninstall"  # not available

SESSION_START_CONTEXT = "sessiononstart"  # "onsessionstart"
SESSION_FINISH_CONTEXT = "sessiononfinish"  # "sessiononfinish"

REQUEST_START_CONTEXT = "requestonstart"  # "onrequeststart"
REQUEST_TIMEOUT_CONTEXT = "requestontimeout"
REQUEST_ERROR_CONTEXT = "requestonerror"

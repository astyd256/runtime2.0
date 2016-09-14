
import re
from __builtin__ import compile as python_compile
from logs import server_log
from memory import PYTHON_EXTENSION, SYMBOLS_EXTENSION, BYTECODE_EXTENSION
from ...wrappers import server, application, session, log, request, response, obsolete_request
from ... import packages
from ..constants import SOURCE_CODE, LISTING, SYMBOLS, BYTECODE


REMOVE_ENCODING_REGEX = re.compile(r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+).*$", re.MULTILINE)
ENCODING_ERROR_MESSAGE = "encoding declaration in Unicode string"


extensions = {
    SOURCE_CODE: PYTHON_EXTENSION,
    LISTING: PYTHON_EXTENSION,
    SYMBOLS: SYMBOLS_EXTENSION,
    BYTECODE: BYTECODE_EXTENSION
}


def cleanup(executable):
    pass


def compile(executable, package, signature, source_code):
    try:
        return python_compile(source_code, signature, "exec")
    except SyntaxError as error:
        if error.msg == ENCODING_ERROR_MESSAGE:
            server_log.warning("Unsuitable encoding declaration into %s, line %s" % (executable, error.lineno))
            source_code = REMOVE_ENCODING_REGEX.sub("", source_code)
            return python_compile(source_code, signature, "exec")


def execute(executable, bytecode, context, namespace):
    if namespace is None:
        namespace = {}

    if context is not None:
        namespace["self"] = context

    namespace.update(
        log=log,
        server=server,
        request=request,
        response=response,
        session=session,
        application=application,
        obsolete_request=obsolete_request,
        packages=packages)

    exec(bytecode, namespace)

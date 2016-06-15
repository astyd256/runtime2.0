
import re

from utils.properties import lazy
from memory import PYTHON_LANGUAGE
from logs import server_log

from ...wrappers import server, application, session, log, request, response, obsolete_request
from ...object import VDOM_object
from .generic import Code


MISSING = "MISSING"
REMOVE_ENCODING_REGEX = re.compile(r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+).*$", re.MULTILINE)
ERROR_MESSAGE = "encoding declaration in Unicode string"


class PythonCode(Code):

    @lazy
    def _scripting_language(self):
        return PYTHON_LANGUAGE

    def _compile(self, store=False):
        try:
            return compile(self._source_code, self._signature, "exec")
        except SyntaxError as error:
            if error.msg == ERROR_MESSAGE:
                self._source_code = REMOVE_ENCODING_REGEX.sub("", self._source_code)
                return self._compile(store=store)
            else:
                server_log.warning("Unable to compile %s, line %s: %s" % (self, error.lineno, error.msg))
                return None

    def _invoke(self, namespace, context=None):
        if self._code is None:
            raise Exception("No code to execute")

        if self._package:
            __import__(self._package)
            namespace["__package__"] = self._package

        namespace.update(
            server=server,
            request=request,
            response=response,
            session=session,
            application=application,
            log=log,
            obsolete_request=obsolete_request,
            VDOM_object=VDOM_object)

        if context:
            namespace["self"] = context
        try:
            exec self._code in namespace
        finally:
            namespace.pop("self", None)

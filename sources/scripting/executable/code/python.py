
from utils.properties import lazy
from memory import PYTHON_LANGUAGE

from ...wrappers import server, application, session, log, request, response, obsolete_request
from ...object import VDOM_object
from .generic import Code


class PythonCode(Code):

    @lazy
    def _scripting_language(self):
        return PYTHON_LANGUAGE

    def _compile(self):
        return compile(self._source_code, self._signature, u"exec"), None

    def _invoke(self, namespace, context=None):
        if self._package:
            __import__(self._package)
            namespace["__package__"] = self._package

        namespace.update(
            self=context,
            server=server,
            request=request,
            response=response,
            session=session,
            application=application,
            log=log,
            obsolete_request=obsolete_request,
            VDOM_object=VDOM_object)

        exec self._code in namespace


from utils.properties import lazy
from memory import VSCRIPT_LANGUAGE
from .generic import Code


vengine = __import__("vscript.engine")


class VScriptCode(Code):

    @lazy
    def _scripting_language(self):
        return VSCRIPT_LANGUAGE

    def _compile(self):
        return vengine.vcompile(self._source_code, filename=self._signature, package=self._package)

    def _invoke(self, namespace, context=None):
        vengine.vexecute(self._code, self._symbols, context, namespace)

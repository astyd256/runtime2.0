
from importlib import import_module
from json import loads, dumps
import settings
from utils.properties import lazy
from memory import PYTHON_EXTENSION, SYMBOLS_EXTENSION, VSCRIPT_LANGUAGE
from .generic import Code


vengine = import_module("vscript.engine")


class VScriptCode(Code):

    @lazy
    def _scripting_language(self):
        return VSCRIPT_LANGUAGE

    def _compile(self, store=False):
        if self._exists(PYTHON_EXTENSION):
            python_source_code = self._read(PYTHON_EXTENSION)
            self._symbols = loads(self._read(SYMBOLS_EXTENSION))
        else:
            python_source_code, self._symbols = vengine.vcompile(self._source_code,
                filename=self._signature, package=self._package, bytecode=0, listing=settings.SHOW_VSCRIPT_LISTING)
            if store:
                self._write(PYTHON_EXTENSION, python_source_code)
                self._write(SYMBOLS_EXTENSION, unicode(dumps(self._symbols)))
        return compile(python_source_code, self._signature, "exec")

    def _invoke(self, namespace, context=None):
        if self._package:
            __import__(self._package)
            namespace["__package__"] = self._package
        vengine.vexecute(self._code, self._symbols, context, namespace)

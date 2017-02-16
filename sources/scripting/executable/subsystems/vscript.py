
from __builtin__ import compile as python_compile
from importlib import import_module
import settings
from memory import VSCRIPT_EXTENSION, PYTHON_EXTENSION, SYMBOLS_EXTENSION, BYTECODE_EXTENSION
from ..constants import LISTING, SYMBOLS, BYTECODE
from ..bytecode import Bytecode


vengine = import_module("vscript.engine")
vcompile, vexecute = vengine.vcompile, vengine.vexecute
pack = import_module("vscript.conversions").pack


class VScriptBytecode(Bytecode):

    __slots__ = ()

    source_extension = VSCRIPT_EXTENSION
    extensions = {BYTECODE: BYTECODE_EXTENSION, LISTING: PYTHON_EXTENSION, SYMBOLS: SYMBOLS_EXTENSION}

    @classmethod
    def compile(cls, executable, signature=None):
        listing, symbols = vcompile(executable.source_code,
            package=executable.package, bytecode=False, listing=settings.SHOW_VSCRIPT_LISTING)
        bytecode = python_compile(listing, signature or executable.signature, "exec")
        return cls(executable, bytecode, listing=listing, symbols=symbols)

    def execute(self, context, namespace, arguments):
        if arguments:
            for name, value in arguments.iteritems():
                namespace["v_%s" % name.replace("_", "")] = pack(value)
        vexecute(self._bytecode, self._symbols, context, namespace)

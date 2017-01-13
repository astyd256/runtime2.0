
from __builtin__ import compile as python_compile
from importlib import import_module
from json import dumps
import settings
from memory import VSCRIPT_EXTENSION, PYTHON_EXTENSION, SYMBOLS_EXTENSION, BYTECODE_EXTENSION
from ..constants import SOURCE_CODE, LISTING, SYMBOLS, BYTECODE


vengine = import_module("vscript.engine")
vcompile, vexecute = vengine.vcompile, vengine.vexecute
pack = import_module("vscript.conversions").pack


extensions = {
    SOURCE_CODE: VSCRIPT_EXTENSION,
    LISTING: PYTHON_EXTENSION,
    SYMBOLS: SYMBOLS_EXTENSION,
    BYTECODE: BYTECODE_EXTENSION
}


def cleanup(executable):
    executable.delete(LISTING)
    executable.delete(SYMBOLS)


def compile(executable, package, signature, source_code):
    listing, symbols = vcompile(source_code,
        package=package, bytecode=False, listing=settings.SHOW_VSCRIPT_LISTING)

    setattr(executable, SYMBOLS, symbols)
    if settings.STORE_BYTECODE:
        executable.write(LISTING, listing)
    if settings.STORE_SYMBOLS:
        executable.write(SYMBOLS, unicode(dumps(symbols)))

    return python_compile(listing, signature, "exec")


def execute(executable, bytecode, context, namespace, arguments):
    if namespace is None:
        namespace = {}

    if arguments is not None:
        for name, value in arguments.iteritems():
            namespace["v_%s" % name.replace("_", "")] = pack(value)

    try:
        symbols = getattr(executable, SYMBOLS)
    except AttributeError:
        symbols = executable.read(SYMBOLS) if settings.STORE_SYMBOLS else None
        if symbols is None:
            executable.compile()
            try:
                symbols = getattr(executable, SYMBOLS)
            except AttributeError:
                raise Exception("Unable to get symbols for %s" % executable)

    vexecute(bytecode, symbols, context, namespace)

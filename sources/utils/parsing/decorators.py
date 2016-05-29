
import new
from .subparsers import native as native_subparser, anyway as anyway_subparser


def native(handler):
    handler.subparser = native_subparser
    return handler


def anyway(handler):
    handler.subparser = anyway_subparser
    return handler


def uncover(function):
    name = function.func_name
    code = function.func_code

    name = name[1:] if name[0] == "_" else name
    arguments = tuple((name[1:] if name[0] == "_" else name)
        for name in code.co_varnames[:code.co_argcount])

    new_code = new.code(
        code.co_argcount,
        code.co_nlocals,
        code.co_stacksize,
        code.co_flags,
        code.co_code,
        code.co_consts,
        code.co_names,
        arguments + code.co_names,
        code.co_filename,
        code.co_name,
        code.co_firstlineno,
        code.co_lnotab)

    print function.func_closure

    new_function = new.function(
        new_code,
        function.func_globals,
        name,
        function.func_defaults,
        function.func_closure)

    return new_function

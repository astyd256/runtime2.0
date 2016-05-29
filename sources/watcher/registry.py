
import types
from . import modules


modules = {function.__name__: function for name, function in
        ((name, getattr(modules, name)) for name in dir(modules))
    if isinstance(function, types.FunctionType)}

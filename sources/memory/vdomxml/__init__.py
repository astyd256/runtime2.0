
from .dumps import dumps
import settings

try:
    if not settings.BINARY_LOADS_EXTENSION:
        raise ImportError
    from ._loads import loads, BaseException as ParsingException
except ImportError:
    from .loads import loads, BaseException as ParsingException

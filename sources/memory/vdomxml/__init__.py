
from .dumps import dumps
import settings

if settings.BINARY_LOADS_EXTENSION:
    try:
        from ._loads import loads
    except ImportError:
        from .loads import loads
else:
    from .loads import loads

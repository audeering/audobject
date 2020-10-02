from audobject import define
from audobject.core.config import config
from audobject.core.parameters import (
    Parameter,
    Parameters,
)
from audobject.core.api import (
    Object,
    TupleResolver,
    ValueResolver,
)


# Disencourage from audobject import *
__all__ = []


# Dynamically get the version of the installed module
try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except Exception:  # pragma: no cover
    pkg_resources = None  # pragma: no cover
finally:
    del pkg_resources

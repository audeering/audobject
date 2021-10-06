from audobject import define
from audobject import resolver
from audobject.core.api import (
    from_dict,
    from_yaml,
    from_yaml_s,
)
from audobject.core.config import config
from audobject.core.parameter import (
    Parameter,
    Parameters,
)
from audobject.core.decorator import (
    init_decorator,
)
from audobject.core.dictionary import (
    Dictionary,
)
from audobject.core.object import (
    Object,
)
from audobject.core.resolver import (
    FilePathResolver,
    FunctionResolver,
    TupleResolver,
    TypeResolver,
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

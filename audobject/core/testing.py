from datetime import datetime

from audobject.core.decorator import (
    init_object_decorator,
)
from audobject.core.object import (
    Object,
)
from audobject.core.resolver import (
    TupleResolver,
)


class TestObject(Object):
    r"""Test object.

    Args:
        name: object name
        point: point with two dimensions
        date: date, if ``None`` initialized with current date
        **kwargs: additional variables

    Example:

    >>> from datetime import datetime
    >>> foo = TestObject('test', date=datetime(1991, 2, 20), var=1.234)
    >>> print(foo)
    $audobject.core.testing.TestObject:
      name: test
      point:
      - 0
      - 0
      date: 1991-02-20 00:00:00
      var: 1.234

    """
    @init_object_decorator({
        'point': TupleResolver,
    })
    def __init__(
            self,
            name: str,
            *,
            point: (int, int) = (0, 0),
            date: datetime = None,
            **kwargs,
    ):
        self.name = name
        self.point = point
        self.date = date or datetime.now()
        for key, value in kwargs.items():
            self.__dict__[key] = value

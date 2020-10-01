from datetime import datetime
from audobject.core.api import Object, TupleResolver


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
      date: '1991-02-20 00:00:00.000000'
      var: 1.234

    """
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
        self._value_resolver['point'] = TupleResolver()
        self.date = date or datetime.now()
        self._value_resolver['date'] = (
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f'),
            lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')
        )
        for key, value in kwargs.items():
            self.__dict__[key] = value

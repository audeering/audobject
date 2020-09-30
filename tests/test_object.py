from datetime import datetime
import os

import pytest

import audobject


class TupleResolver(audobject.ValueResolver):

    def encode(self, value: tuple) -> list:
        return list(value)

    def decode(self, value: list) -> tuple:
        return tuple(value)


class MyObject(audobject.Object):
    def __init__(self, **kwargs):
        self._value_resolver['tuple'] = TupleResolver()
        self._value_resolver['time'] = (
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f'),
            lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')
        )
        for key, value in kwargs.items():
            self.__dict__[key] = value


@pytest.mark.parametrize(
    'variables',
    [
        {
            'dict': {'a': 1, 'b': 2, 'c': 3},
            'float': 1.0,
            'int': 0,
            'list': [1, 2, 3],
            'none': None,
            'object': MyObject(foo='bar'),
            'string': 'abc',
            'time': datetime.now(),
            'tuple': (1, '2', [3, 4, 5]),
        },
    ]
)
def test(tmpdir, variables):
    t = MyObject(**variables)
    assert t == t.from_yaml_s(t.to_yaml_s())
    path = os.path.join(tmpdir, 'test.yaml')
    t.to_yaml(path)
    t2 = audobject.Object.from_yaml(path)
    assert t == t2
    assert repr(t) == repr(t2)
    assert str(t) == str(t2)
    assert t.to_yaml_s() == t2.to_yaml_s()
    for key, value in t.__dict__.items():
        assert t2.__dict__[key] == value


@pytest.mark.parametrize(
    'variables',
    [
        {
            'no_encoder': (1, 2, 3),
        },
    ]
)
def test_no_encoder(tmpdir, variables):
    t = MyObject(**variables)
    with pytest.warns(RuntimeWarning):
        t.to_yaml_s()
    path = os.path.join(tmpdir, 'test.yaml')
    t.to_yaml(path)
    t2 = audobject.Object.from_yaml(path)
    for key, value in t.__dict__.items():
        assert t2.__dict__[key] != value

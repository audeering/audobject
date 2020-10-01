from datetime import datetime
import os

import pytest

import audobject
import audobject.testing


class MyObject(audobject.Object):
    def __init__(self, **kwargs):
        self._value_resolver['tuple'] = audobject.TupleResolver()
        self._value_resolver['time'] = (
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f'),
            lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')
        )
        for key, value in kwargs.items():
            self.__dict__[key] = value


@pytest.mark.parametrize(
    'obj',
    [
        audobject.testing.TestObject(
            'test',
            d={'a': 1, 'b': 2, 'c': 3},
            f=1.0,
            i=0,
            l=[1, 2, 3],
            n=None,
            o=audobject.testing.TestObject('another'),
        ),
    ]
)
def test(tmpdir, obj):
    assert obj == obj.from_yaml_s(obj.to_yaml_s())
    path = os.path.join(tmpdir, 'test.yaml')
    obj.to_yaml(path)
    t2 = audobject.Object.from_yaml(path)
    assert obj == t2
    assert repr(obj) == repr(t2)
    assert str(obj) == str(t2)
    assert obj.to_yaml_s() == t2.to_yaml_s()
    for key, value in obj.__dict__.items():
        assert t2.__dict__[key] == value


def test_no_encoder(tmpdir):
    obj = audobject.testing.TestObject(
        'test',
        no_encoder=(1, 2, 3),
    )
    with pytest.warns(RuntimeWarning):
        obj.to_yaml_s()
    path = os.path.join(tmpdir, 'test.yaml')
    obj.to_yaml(path)
    obj2 = audobject.Object.from_yaml(path)
    assert obj.no_encoder != obj2.no_encoder

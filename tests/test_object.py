import os

import pytest

import audobject
import audobject.testing


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
    assert obj == audobject.Object.from_yaml_s(obj.to_yaml_s())
    path = os.path.join(tmpdir, 'test.yaml')
    obj.to_yaml(path)
    t2 = audobject.Object.from_yaml(path)
    assert obj == t2
    assert repr(obj) == repr(t2)
    assert str(obj) == str(t2)
    assert obj.to_yaml_s() == t2.to_yaml_s()
    for key, value in obj.__dict__.items():
        if not key.strip('_'):
            assert t2.__dict__[key] == value


def test_no_encoder(tmpdir):
    obj = audobject.testing.TestObject(
        'test',
        no_encoder=(1, 2, 3),
    )
    path = os.path.join(tmpdir, 'test.yaml')
    with pytest.warns(RuntimeWarning):
        obj.to_yaml(path)

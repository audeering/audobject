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
            d_empty={},
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


class ObjectWithHiddenArguments(audobject.Object):

    @audobject.init_decorator(
        hide=['hidden']
    )
    def __init__(
            self,
            string: str,
            *,
            hidden: str = None,
    ):
        self.string = string
        self.hidden = hidden


def test_hidden_attributes():

    o = ObjectWithHiddenArguments('test', hidden='hidden')
    assert o.hidden == 'hidden'
    o2 = audobject.Object.from_yaml_s(o.to_yaml_s(include_version=False))
    assert isinstance(o2, ObjectWithHiddenArguments)
    assert o2.hidden is None


def test_override_attributes():

    o = audobject.testing.TestObject(name='name')
    assert o.name == 'name'
    o2 = audobject.Object.from_yaml_s(
        o.to_yaml_s(),
        name='override',
    )
    assert isinstance(o2, audobject.testing.TestObject)
    assert o2.name == 'override'


def test_no_resolver(tmpdir):

    obj = audobject.testing.TestObject(
        'test',
        no_encoder=(1, 2, 3),
    )
    path = os.path.join(tmpdir, 'test.yaml')
    with pytest.warns(RuntimeWarning):
        obj.to_yaml(path)


def test_bad_object():

    class BadObject(audobject.Object):
        def __init__(
                self,
                foo: str = None,
        ):
            self.bar = foo

    o = BadObject('foo')
    with pytest.raises(RuntimeError):
        o.to_yaml_s()  # argument foo not assigned to an attribute

    class BadObject(audobject.Object):
        @audobject.init_decorator(
            hide=['foo'],
        )
        def __init__(
                self,
                foo: str,
        ):
            self.bar = foo

    with pytest.raises(RuntimeError):
        BadObject('foo')  # cannot hide argument without default value

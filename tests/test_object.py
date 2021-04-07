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
    # test hashable collection
    assert hash(obj) == hash(obj.id)
    set().add(obj)


class Point:
    def __init__(
            self,
            x: int,
            y: int,
    ):
        self.x = x
        self.y = y


class ObjectWithBorrowedArguments(audobject.Object):

    @audobject.init_decorator(
        borrow={
            'x': 'point',
            'y': 'point',
            'z': 'd',
        },
    )
    def __init__(
            self,
            x: int,
            y: int,
            z: int,
    ):
        self.point = Point(x, y)
        self.d = {'z': z}


def test_borrowed():
    x = 0
    y = 1
    z = 2
    o = ObjectWithBorrowedArguments(x, y, z)
    assert x not in o.__dict__
    assert y not in o.__dict__
    assert z not in o.__dict__
    assert o.point.x == x
    assert o.point.y == y
    assert o.d['z'] == z
    o2 = audobject.Object.from_yaml_s(o.to_yaml_s(include_version=False))
    assert isinstance(o2, ObjectWithBorrowedArguments)
    assert x not in o2.__dict__
    assert y not in o2.__dict__
    assert z not in o2.__dict__
    assert o2.point.x == x
    assert o2.point.y == y
    assert o.d['z'] == z


@pytest.mark.parametrize(
    'obj, expected',
    [
        (
            audobject.testing.TestObject(
                'test',
                point=(1, 1),
                foo={},
                bar=[],
            ),
            {
                'name': 'test',
                'point.0': 1,
                'point.1': 1,
            }
        ),
        (
            audobject.testing.TestObject(
                'test',
                point=(1, 1),
                object=audobject.testing.TestObject(
                    'test',
                    foo='foo',
                    point=(2, 2),
                    list=[
                        audobject.testing.TestObject(
                            'test',
                            point=(3, 3),
                        ),
                        'foo',
                    ],
                    dict={
                        'object': audobject.testing.TestObject(
                            'test',
                            bar='bar',
                            point=(4, 4),
                        ),
                        'foo': 'foo',
                    }
                )
            ),
            {
                'name': 'test',
                'point.0': 1,
                'point.1': 1,
                'object.name': 'test',
                'object.point.0': 2,
                'object.point.1': 2,
                'object.foo': 'foo',
                'object.list.0.name': 'test',
                'object.list.0.point.0': 3,
                'object.list.0.point.1': 3,
                'object.list.1': 'foo',
                'object.dict.object.name': 'test',
                'object.dict.object.point.0': 4,
                'object.dict.object.point.1': 4,
                'object.dict.object.bar': 'bar',
                'object.dict.foo': 'foo'
            },
        ),
    ]
)
def test_flatten(obj, expected):
    assert obj.to_dict(flatten=True) == expected


class ParentWithHiddenArguments(audobject.Object):

    @audobject.init_decorator(
        hide=['hidden_parent']
    )
    def __init__(
            self,
            hidden_parent: str = None,
    ):
        self.hidden_parent = hidden_parent


class ChildWithHiddenArguments(ParentWithHiddenArguments):

    @audobject.init_decorator(
        hide=['hidden_child']
    )
    def __init__(
            self,
            string: str,
            *,
            hidden_child: str = None,
            hidden_parent: str = None,
    ):
        super().__init__(hidden_parent)
        self.string = string
        self.hidden_child = hidden_child


def test_hidden_attributes(tmpdir):

    path = os.path.join(tmpdir, 'test.yaml')

    o = ChildWithHiddenArguments(
        'test',
        hidden_child='hidden_child',
        hidden_parent='hidden_parent',
    )
    assert o.hidden_child == 'hidden_child'
    assert o.hidden_parent == 'hidden_parent'

    o2 = audobject.Object.from_yaml_s(o.to_yaml_s(include_version=False))
    assert isinstance(o2, ChildWithHiddenArguments)
    assert o2.hidden_child is None
    assert o2.hidden_parent is None

    o.to_yaml(path, include_version=False)
    o2 = audobject.Object.from_yaml(path)
    assert isinstance(o2, ChildWithHiddenArguments)
    assert o2.hidden_child is None

    o2 = audobject.Object.from_yaml_s(
        o.to_yaml_s(include_version=False),
        hidden_child='hidden_child',
        hidden_parent='hidden_parent',
    )
    assert isinstance(o2, ChildWithHiddenArguments)
    assert o2.hidden_child == 'hidden_child'
    assert o2.hidden_parent == 'hidden_parent'

    o.to_yaml(path, include_version=False)
    o2 = audobject.Object.from_yaml(
        path,
        hidden_child='hidden_child',
        hidden_parent='hidden_parent',
    )
    assert isinstance(o2, ChildWithHiddenArguments)
    assert o2.hidden_child == 'hidden_child'
    assert o2.hidden_parent == 'hidden_parent'


def test_override_attributes():

    o = audobject.testing.TestObject(name='name')
    assert o.name == 'name'
    o2 = audobject.Object.from_yaml_s(
        o.to_yaml_s(),
        name='override',
    )
    assert isinstance(o2, audobject.testing.TestObject)
    assert o2.name == 'override'


def test_no_resolver():

    obj = audobject.testing.TestObject(
        'test',
        no_encoder=(1, 2, 3),
    )
    with pytest.warns(RuntimeWarning):
        obj.to_yaml_s()

    obj = audobject.testing.TestObject(
        'test',
        no_encoder=lambda x: x,
    )
    with pytest.raises(RuntimeError):
        obj.to_yaml_s()

    def func():
        pass

    obj = audobject.testing.TestObject(
        'test',
        no_encoder=func,
    )
    with pytest.raises(RuntimeError):
        obj.to_yaml_s()

    obj = audobject.testing.TestObject(
        'test',
        no_encoder=[func],
    )
    with pytest.raises(RuntimeError):
        obj.to_yaml_s()

    obj = audobject.testing.TestObject(
        'test',
        no_encoder={'func': func},
    )
    with pytest.raises(RuntimeError):
        obj.to_yaml_s()


def test_bad_object():

    class BadObject(audobject.Object):
        def __init__(
                self,
                foo: str = None,
        ):
            self.bar = foo

    o = BadObject('foo')
    with pytest.raises(RuntimeError):
        with pytest.warns(RuntimeWarning):
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
        with pytest.warns(RuntimeWarning):
            BadObject('foo')  # cannot hide argument without default value

    class BadObject(audobject.Object):
        @audobject.init_decorator(
            borrow={
                'x': 'point',
                'y': 'point',
            },
        )
        def __init__(
                self,
                x: int,
                y: int,
        ):
            pass

    with pytest.raises(RuntimeError):
        with pytest.warns(RuntimeWarning):
            BadObject(0, 1).to_yaml_s()  # cannot borrow from missing attribute

    class BadObject(audobject.Object):
        @audobject.init_decorator(
            borrow={
                'x': 'point',
                'y': 'point',
            },
        )
        def __init__(
                self,
                x: int,
                y: int,
        ):
            self.point = 0

    with pytest.raises(RuntimeError):
        with pytest.warns(RuntimeWarning):
            BadObject(0, 1).to_yaml_s()  # cannot borrow missing attribute

    class BadObject(audobject.Object):
        @audobject.init_decorator(
            borrow={
                'x': 'point',
                'y': 'point',
                'z': 'point',
            },
        )
        def __init__(
                self,
                x: int,
                y: int,
        ):
            self.point = Point(x, y)

    with pytest.raises(RuntimeError):
        with pytest.warns(RuntimeWarning):
            BadObject(0, 1).to_yaml_s()  # cannot borrow missing attribute

import os
import shutil
import typing

import audeer

import audobject


class ObjectWithFile(audobject.Object):

    @audobject.init_decorator(
        resolvers={
            'path': audobject.resolver.FilePath,
        }
    )
    def __init__(
            self,
            path: str,
    ):
        self.path = path


def test_filepath(tmpdir):

    root = os.path.join(tmpdir, 'test')
    new_root = os.path.join(tmpdir, 'some', 'where', 'else')

    # create resource file
    resource_path = os.path.join(root, 're', 'source.txt')
    audeer.mkdir(os.path.dirname(resource_path))
    with open(resource_path, 'w'):
        pass

    # create object and serialize
    yaml_path = os.path.join(root, 'yaml', 'object.yaml')
    o = ObjectWithFile(resource_path)
    o.to_yaml(yaml_path, include_version=False)

    # move files to another location
    shutil.move(root, new_root)
    new_yaml_path = os.path.join(new_root, 'yaml', 'object.yaml')

    # re-instantiate object from new location and assert path exists
    o2 = audobject.from_yaml(new_yaml_path)
    assert isinstance(o2, ObjectWithFile)
    assert os.path.exists(o2.path)


class ObjectWithFunction(audobject.Object):

    @audobject.init_decorator(
        resolvers={
            'fun1': audobject.resolver.Function,
            'fun2': audobject.resolver.Function,
        }
    )
    def __init__(
            self,
            fun1: typing.Callable,
            fun2: typing.Callable,
    ):
        self.fun1 = fun1
        self.fun2 = fun2

    def __call__(self, *args, **kwargs):
        return self.fun1(*args, **kwargs) + self.fun2(*args, **kwargs)


def test_function(tmpdir):

    def square(x):
        return x * x

    o = ObjectWithFunction(
        fun1=square,
        fun2=lambda x: -(x * x),
    )

    path = os.path.join(tmpdir, 'foo.yaml')
    o.to_yaml(path, include_version=False)
    o2 = audobject.from_yaml(path)

    assert o(10) == o2(10) == 0

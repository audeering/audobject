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
            'func': audobject.resolver.Function,
        }
    )
    def __init__(
            self,
            func: typing.Callable,
    ):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def test_function(tmpdir):

    # lambda

    o_lambda = ObjectWithFunction(lambda x: x * x)

    path = os.path.join(tmpdir, 'lambda.yaml')
    o_lambda.to_yaml(path, include_version=False)
    o_lambda_2 = audobject.from_yaml(path)

    assert o_lambda(10) == o_lambda_2(10) == 10 * 10
    assert o_lambda.to_yaml_s(include_version=False) == \
           o_lambda_2.to_yaml_s(include_version=False)

    # function with single positional argument

    def func(a):
        return a + 1

    o_func = ObjectWithFunction(func)

    path = os.path.join(tmpdir, 'func.yaml')
    o_func.to_yaml(path, include_version=False)
    o_func_2 = audobject.from_yaml(path)

    assert func(10) == o_func(10) == o_func_2(10)
    assert func(10) == o_func(10) == o_func_2(10)
    assert func(10) == o_func(10) == o_func_2(10)
    assert o_func.to_yaml_s(include_version=False) == \
           o_func_2.to_yaml_s(include_version=False)
    assert func.__defaults__ == o_func_2.func.__defaults__
    assert func.__kwdefaults__ == o_func_2.func.__kwdefaults__

    # function with defaults and keyword-only argument

    def func_ex(a, b=0, *, c=0):
        return a + b + c

    o_func_ex = ObjectWithFunction(func_ex)

    path = os.path.join(tmpdir, 'func-ex.yaml')
    o_func_ex.to_yaml(path, include_version=False)
    o_func_ex_2 = audobject.from_yaml(path)

    assert func_ex(10) == o_func_ex(10) == o_func_ex_2(10)
    assert func_ex(10, 20) == o_func_ex(10, 20) == o_func_ex_2(10, 20)
    assert func_ex(10, 20, c=30) == o_func_ex(10, 20, c=30) == \
           o_func_ex_2(10, 20, c=30)
    assert o_func_ex.to_yaml_s(include_version=False) == \
           o_func_ex_2.to_yaml_s(include_version=False)
    assert func_ex.__defaults__ == o_func_ex_2.func.__defaults__
    assert func_ex.__kwdefaults__ == o_func_ex_2.func.__kwdefaults__

import argparse
import os

import parse
import pytest

import audobject


@pytest.mark.parametrize(
    'dtype,default,choices,value',
    [
        (str, None, None, None),
        (str, 'default', None, 'value'),
        (str, 'default', ['default', 'value'], 'value'),
        (int, 0, [0, 1], 1),
        (str, None, [None, 'value'], 'value'),
        pytest.param(  # wrong value type
            str, 'default', None, 5,
            marks=pytest.mark.xfail(raises=TypeError),
        ),
        pytest.param(  # value not in choices
            str, 'default', ['default'], 'value',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(  # default not in choices
            str, None, ['value'], 'value',
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ]
)
def test_parameter_type(dtype, default, choices, value):
    p = audobject.Parameter(
        name='foo',
        dtype=dtype,
        description='bar',
        default=default,
        choices=choices,
    )
    assert p.value == default
    p.set_value(value)
    assert p.value == value


@pytest.mark.parametrize(
    'param_version,check_version,result',
    [
        (None, None, True),
        (None, '1.0.0', True),
        ('==1.0.0', None, True),
        ('==1.0.0', '1.0.0', True),
        ('==1.0.0', '2.0.0', False),
        ('>=1.0.0', '2.0.0', True),
        ('>=2.0.0', '2.0.0', True),
        ('>2.0.0', '2.0.0', False),
        ('>=1.0.0,<2.0.0', '2.0.0', False),
        ('>=1.0.0,!=2.0.0', '2.0.0', False),
        ('>=1.0.0,<3.0.0', '2.0.0', True),
        ('>=1.0.0,<3.0.0,!=2.0.0', '2.0.0', False),
    ]
)
def test_parameter_version(param_version, check_version, result):
    p = audobject.Parameter(
        name='foo',
        dtype=str,
        description='bar',
        version=param_version,
    )
    assert result == (check_version in p)


@pytest.mark.parametrize(
    'params',
    [
        (
            []
        ),
        (
            [
                audobject.Parameter(name='foo', dtype=str, description='bar'),
                audobject.Parameter(name='idx', dtype=int, description='int')
            ]
        ),
    ]
)
def test_parameters_init(params):
    pp = audobject.Parameters()
    for p in params:
        pp.add(p)
    for p in params:
        assert p.name in pp.keys()
        assert p in pp.values()
    for key, value in pp.items():
        assert key in pp.keys()
        assert value in pp.values()


def test_parameters_command_line():

    p = pytest.PARAMETERS
    old_value = p.bar
    new_value = old_value + 1

    parser = argparse.ArgumentParser()
    p.to_command_line(parser)

    args = parser.parse_args(args=[f'--bar={new_value}', '--toggle'])

    assert p.foo == args.foo
    assert p.bar != args.bar
    assert p.toggle is False
    p.from_command_line(args)
    assert p.bar == args.bar
    assert p.toggle is True

    parser = argparse.ArgumentParser()
    p.to_command_line(parser, version='1.0.0')
    with pytest.raises(SystemExit):
        parser.parse_args(args=[f'--bar={new_value}'])


def test_parameters_dict():

    p = pytest.PARAMETERS
    old_value = p.bar
    new_value = old_value + 1

    d = p.to_dict()
    assert d['bar'] == p.bar
    d['bar'] = new_value
    assert p.bar == old_value

    p.from_dict(d)
    assert p.bar == new_value

    assert list(d) == ['foo', 'bar', 'toggle']
    d = p.to_dict(sort=True)
    assert list(d) == ['bar', 'foo', 'toggle']

    assert 'bar' in d
    d = p.to_dict(version='1.0.0')
    assert 'bar' not in d


def test_parameters_path():

    p = pytest.PARAMETERS

    path = p.to_path(delimiter=',')
    for item in path.split(','):
        key, value = parse.parse('{}[{}]', item)
        assert str(p.get_parameter(key).value) == value

    path = p.to_path(delimiter=',', include=['bar'])
    assert 'bar' in path
    assert 'foo' not in path
    path = p.to_path(delimiter=',', exclude=['bar'])
    assert 'bar' not in path
    assert 'foo' in path


def test_parameters_value():

    p = pytest.PARAMETERS
    old_value = p.get_parameter('bar').value
    new_value = old_value + 1

    assert p.bar == old_value
    p.bar = new_value
    assert p.bar == new_value


def test_parameters_yaml(tmpdir):

    p = pytest.PARAMETERS
    file = os.path.join(tmpdir, 'params.yaml')
    old_value = p.bar
    new_value = old_value + 1

    p.to_yaml(file)
    p.bar = new_value
    assert p.bar != old_value
    p.from_yaml(file)
    assert p.bar == old_value

    p.bar = new_value
    p.to_yaml(file)
    p.from_yaml(file)
    assert p.bar == new_value

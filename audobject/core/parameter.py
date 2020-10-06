import argparse
import os
import pkg_resources
import typing

from audobject.core.decorator import (
    init_object_decorator,
)
from audobject.core.object import (
    Object,
)
from audobject.core.resolver import (
    TypeResolver,
)


class Parameter(Object):
    r"""Single parameter.

    A parameter steers the behaviour of a an object (e.g. tuning a model).
    It has a specific type and default value, possibly one of a set of choices.
    It is possible to bound a parameter to a specific version (range).

    Args:
        value_type: data type, one of
            (``None``, ``str``, ``int``, ``float``, ``bool``)
            or a ``list`` or ``dict`` of those
        description: description
        value: value, if ``None`` set to ``default_value``
        default_value: default value
        choices: list with choices
        version: string defining in which versions the parameter is used
            (e.g. ``'>=1.0.0,<2.0.0,!=1.5.0'``),
            ``None`` matches any version

    Raises:
        TypeError: if value has an invalid type
        ValueError: if value is not in choices

    Example:
        >>> foo = Parameter(
        ...     value_type=str,
        ...     description='some parameter',
        ...     default_value='bar',
        ...     choices=['bar', 'Bar', 'BAR'],
        ...     version='>=1.0.0,<2.0.0',
        ... )
        >>> # check version
        >>> '1.5.0' in foo
        True
        >>> '2.0.0' in foo
        False
        >>> # get/set value
        >>> foo.value
        'bar'
        >>> foo.set_value('Bar')
        >>> foo.value
        'Bar'
        >>> # set invalid value
        >>> try:
        ...     foo.set_value('par')
        ... except ValueError as ex:
        ...     print(ex)
        Invalid value 'par', expected one of ['bar', 'Bar', 'BAR'].

    """  # noqa: E501

    @init_object_decorator({
        'value_type': TypeResolver,
    })
    def __init__(
            self,
            *,
            value_type: type = str,
            description: str = '',
            value: typing.Any = None,
            default_value: typing.Any = None,
            choices: typing.Sequence[typing.Any] = None,
            version: str = None,
    ):

        self.value_type = value_type
        r"""Data type of parameter"""
        self.description = description
        r"""Value of parameter, use 'set_value' for type checking"""
        self.value = None
        r"""Description of parameter"""
        self.default_value = default_value
        r"""Default value of parameter"""
        self.choices = choices
        r"""Possible choices for parameter"""
        self.version = version
        r"""Versions in which the parameter is used"""

        if value is not None:
            self.set_value(value)
        else:
            self.set_value(default_value)

    def __contains__(self, version: typing.Optional[str]) -> bool:

        if version is None or self.version is None:
            return True

        v = pkg_resources.parse_version(version)
        r = pkg_resources.Requirement.parse('param' + self.version)

        return v in r

    def set_value(self, value: typing.Any):
        r"""Sets a new value.

        Applies additional checks, e.g. if value is of the expected type.

        Args:
            value: new value

        Raises:
            TypeError: if value has an invalid type
            ValueError: if value is not in choices

        """
        if value is not None and not isinstance(value, self.value_type):
            raise TypeError(
                f"Invalid type '{type(value)}', "
                f"expected {self.value_type}."
            )
        if self.choices is not None and value not in self.choices:
            raise ValueError(
                f"Invalid value '{value}', "
                f"expected one of {self.choices}."
            )
        self.value = value


class Parameters(Object):
    r"""List of parameters.

    Args:
        *args: :class:`audobject.Parameter` objects
        **kwargs: :class:`audobject.Parameter` objects

    Example:
        >>> # create list of parameters
        >>> params = Parameters()
        >>> # create parameter
        >>> foo = Parameter(
        ...     value_type=str,
        ...     description='foo',
        ... )
        >>> # add parameter to list
        >>> params['foo'] = foo
        >>> params['foo']
        {'$audobject.core.parameter.Parameter': {'value_type': 'str', 'description': 'foo', 'value': None, 'default_value': None, 'choices': None, 'version': None}}
        >>> # get / set parameter value
        >>> params.foo = 'bar'
        >>> params.foo
        'bar'

    """  # noqa: E501
    def __init__(
            self,
            **kwargs,
    ):
        for name, param in kwargs.items():
            self[name] = param

    def from_dict(
            self,
            d: typing.Dict[str, typing.Any],
    ) -> 'Parameters':
        r"""Update parameter values from a dictionary.

        .. note:: Ignores keys that are not in the list of parameters.

        Args:
            d: dictionary with new values

        """
        for key, value in d.items():
            if key in self.keys():
                self.__setattr__(key, value)
        return self

    def filter_by_version(
            self,
            version: str,
    ) -> 'Parameters':
        r"""Filter parameters by version.

        Returns a subset including only those parameters that match a given
        version.

        Args:
            version: version string

        Returns:
            List with matching parameters

        """
        params = Parameters()
        for name, param in self.items():
            if version in param:
                params[name] = param
        return params

    def from_command_line(
            self,
            args: argparse.Namespace,
    ) -> 'Parameters':
        r"""Parse parameters from command line parser.

        Args:
            args: command line arguments

        """
        return self.from_dict(args.__dict__)

    def keys(self) -> typing.KeysView[str]:
        r"""Returns the parameter keys."""
        return self.__dict__.keys()

    def items(self) -> typing.ItemsView[str, Parameter]:
        r"""Returns the parameter values."""
        return self.__dict__.items()

    def to_command_line(
            self,
            parser: argparse.ArgumentParser,
    ):
        r"""Add parameters to command line parser.

        .. note:: Command line arguments are named --<name>.

        Args:
            parser: command line parser

        """
        for name, param in self.items():

            if param.version is not None:
                help = f'{param.description} (version: {param.version})'
            else:
                help = param.description

            if param.value_type == bool:
                parser.add_argument(
                    f'--{name}',
                    action='store_true',
                    help=help,
                )
            else:
                parser.add_argument(
                    f'--{name}',
                    type=param.value_type,
                    default=param.default_value,
                    choices=param.choices,
                    help=help,
                )

    def to_path(
            self,
            *,
            delimiter: str = os.path.sep,
            include: typing.Sequence[str] = None,
            exclude: typing.Sequence[str] = None,
            sort: bool = False,
    ):
        r"""Creates path from parameters.

        Args:
            delimiter: delimiter character
            include: list of parameters to include
            exclude: list of parameters to exclude
            sort: sort parameters by name

        """
        names = self.keys()
        if sort:
            names = sorted(names)
        d = {
            name: self[name].value for name in names
        }
        exclude = set(exclude or [])
        if include is not None:
            for key in d:
                if key not in include:
                    exclude.add(key)
        for key in exclude:
            d.pop(key)
        parts = ['{}[{}]'.format(key, value) for key, value in d.items()]
        return delimiter.join(parts)

    def values(self) -> typing.ValuesView[typing.Any]:
        r"""Returns parameter values.

        """
        return self.__dict__.values()

    def __getattribute__(self, name) -> typing.Any:
        if not name == '__dict__' and name in self.__dict__:
            p = self.__dict__[name]
            return p.value
        return object.__getattribute__(self, name)

    def __getitem__(self, name: str) -> Parameter:
        return self.__dict__[name]

    def __repr__(self):  # pragma: no cover
        return str({name: param.value for name, param in self.items()})

    def __setattr__(self, name: str, value: typing.Any):
        p = self.__dict__[name]
        p.set_value(value)

    def __setitem__(self, name: str, param: Parameter):
        self.__dict__[name] = param

    def __str__(self):  # pragma: no cover
        table = [
            [
                'Name', 'Value', 'Default', 'Choices',
                'Description', 'Version',
            ],
            [
                '----', '-----', '-------', '-------',
                '-----------', '-------',
            ]
        ]
        for name, p in self.items():
            table.append(
                [
                    name, p.value, p.default_value, p.choices,
                    p.description, p.version,
                ]
            )
        padding = 2
        # Longest string in each column
        transposed_table = [list(x) for x in zip(*table)]
        col_width = [
            len(max([str(word) for word in row], key=len)) + padding
            for row in transposed_table
        ]
        # Don't pad the last column
        col_width[-1] -= padding
        row = [
            ''.join(
                str(word).ljust(width) for word, width in zip(row, col_width)
            )
            for row in table
        ]
        return '\n'.join(row)

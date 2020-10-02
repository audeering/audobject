import argparse
import os
import pkg_resources
import typing
import oyaml as yaml


class Parameter:
    r"""Single parameter.

    A parameter steers the behaviour of a an object (e.g. tuning a model).
    It has a specific type and default value, possibly one of a set of choices.
    It is possible to bound a parameter to a specific version (range).

    Args:
        name: name
        dtype: data type
        description: description
        default: default value
        choices: list with choices
        version: string defining in which versions the parameter is used
            (e.g. ``'>=1.0.0,<2.0.0,!=1.5.0'``),
            ``None`` matches any version

    Raises:
        TypeError: if value has an invalid type
        ValueError: if value is not in choices

    Example:
        >>> foo = Parameter(
        ...     name='foo',
        ...     dtype=str,
        ...     description='some parameter',
        ...     default='bar',
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
        Invalid value 'par' for parameter foo, expected one of ['bar', 'Bar', 'BAR'].

    """  # noqa: E501

    def __init__(
            self,
            *,
            name: str,
            dtype: type,
            description: str,
            default: typing.Any = None,
            choices: typing.Sequence[typing.Any] = None,
            version: str = None,
    ):

        self.name = name
        r"""Name of parameter"""
        self.dtype = dtype
        r"""Data type of parameter"""
        self.description = description
        r"""Description of parameter"""
        self.default = default
        r"""Default value of parameter"""
        self.choices = choices
        r"""Possible choices for parameter"""
        self.version = version
        r"""Versions in which the parameter is used"""

        self._value = None
        self.set_value(default)

    @property
    def value(self) -> typing.Any:
        r"""Returns the current value."""
        return self._value

    def __repr__(self) -> str:  # pragma: no cover
        return str({self.name: self.value})

    def __str__(self) -> str:  # pragma: no cover
        return str(self.__dict__)

    def __contains__(self, version: typing.Optional[str]) -> bool:

        if version is None or self.version is None:
            return True

        v = pkg_resources.parse_version(version)
        r = pkg_resources.Requirement.parse('param' + self.version)

        return v in r

    def set_value(self, value: typing.Any):
        r"""Sets a new value.

        Args:
            value: new value

        Raises:
            TypeError: if value has an invalid type
            ValueError: if value is not in choices

        """
        if value is not None and not isinstance(value, self.dtype):
            raise TypeError(
                f"Invalid type '{type(value)}' for parameter {self.name}, "
                f"expected {self.dtype}."
            )
        if self.choices is not None and value not in self.choices:
            raise ValueError(
                f"Invalid value '{value}' for parameter {self.name}, "
                f"expected one of {self.choices}."
            )
        self._value = value


class Parameters:
    r"""List of parameters.

    Example:
        >>> # create list of parameters
        >>> params = Parameters()
        >>> # create parameter
        >>> foo = Parameter(
        ...     name='foo',
        ...     dtype=str,
        ...     description='foooo',
        ... )
        >>> # add parameter to list
        >>> params.add(foo)
        {'foo': None}
        >>> # get/set parameter through list
        >>> params.foo
        >>> params.foo = 'foo'
        >>> params.foo
        'foo'

    """

    def add(
            self,
            param: Parameter,
    ) -> 'Parameters':
        r"""Adds a new parameter.

        You can get and set values of an added parameter
        via :attr:`params.name`
        and :attr:`params.name = new_value`.

        Args:
            param: parameter

        """
        self.__dict__[param.name] = param
        return self

    def from_dict(self, d: typing.Dict[str, typing.Any]) -> 'Parameters':
        r"""Update parameter values from a dictionary.

        .. note:: Ignores keys that are not in the list of parameters.

        Args:
            d: dictionary with new values

        """
        for key, value in d.items():
            if key in self.keys():
                self.__setattr__(key, value)
        return self

    def get_parameter(self, name: str) -> Parameter:
        r"""Returns the parameter object."""
        return self.__dict__[name]

    def from_command_line(
            self,
            args: argparse.Namespace,
    ) -> 'Parameters':
        r"""Parse parameters from command line parser.

        Args:
            args: command line arguments

        """
        return self.from_dict(args.__dict__)

    def from_yaml(
            self,
            file: str,
    ) -> 'Parameters':
        with open(file, 'r') as fp:
            d = yaml.load(fp, Loader=yaml.Loader)
            self.from_dict(d)
        return self

    def keys(self) -> typing.KeysView[str]:
        r"""Returns the parameter keys."""
        return self.__dict__.keys()

    def items(self) -> typing.ItemsView[str, Parameter]:
        r"""Returns the parameter values."""
        return self.__dict__.items()

    def to_command_line(
            self,
            parser: argparse.ArgumentParser,
            *,
            version: str = None,
    ):
        r"""Add parameters to command line parser.

        .. note:: Command line arguments are named --<name>.

        Args:
            parser: command line parser
            version: version string (only matching parameters are included)

        """
        for name, param in self.items():

            if version not in param:
                continue

            if param.version is not None:
                help = f'{param.description} (version: {param.version})'
            else:
                help = param.description

            if param.dtype == bool:
                parser.add_argument(
                    f'--{name}',
                    action='store_true',
                    help=help,
                )
            else:
                parser.add_argument(
                    f'--{name}',
                    type=param.dtype,
                    default=param.default,
                    choices=param.choices,
                    help=help,
                )

    def to_dict(
            self,
            *,
            sort: bool = False,
            version: str = None,
    ) -> typing.Dict[str, typing.Any]:
        r"""Returns parameters as dictionary.

        Args:
            sort: sort parameters by name
            version: version string (only matching parameters are included)

        """
        names = [p.name for p in self.values() if version in p]
        if sort:
            names = sorted(names)
        return {
            name: self.get_parameter(name).value for name in names
        }

    def to_path(
            self,
            *,
            delimiter: str = os.path.sep,
            include: typing.Sequence[str] = None,
            exclude: typing.Sequence[str] = None,
            sort: bool = False,
            version: str = None,
    ):
        r"""Creates path from parameters.

        Args:
            delimiter: delimiter character
            include: list of parameters to include
            exclude: list of parameters to exclude
            sort: sort parameters by name
            version: version string (only matching parameters are included)

        """
        d = self.to_dict(sort=sort, version=version)
        exclude = set(exclude or [])
        if include is not None:
            for key in d:
                if key not in include:
                    exclude.add(key)
        for key in exclude:
            d.pop(key)
        parts = ['{}[{}]'.format(key, value) for key, value in d.items()]
        return delimiter.join(parts)

    def to_yaml(
            self,
            file: str,
            *,
            sort: bool = False,
            version: str = None,
            force_create: bool = False,
    ):
        r"""Writes parameters to a yaml file.

        .. note:: If file exists its content will be updated. Except if
            ``force_create`` is set, in that case the file will always be
            created.

        Args:
            file: file path
            sort: sort parameters by name
            version: version string (only matching parameters will be written)
            force_create: create file even if it exists

        """
        p = self.to_dict(sort=sort, version=version)

        if not force_create and os.path.exists(file):
            with open(file, 'r') as fp:
                d = yaml.load(fp, Loader=yaml.Loader)
                for key, value in p.items():
                    d[key] = value
        else:
            d = p

        with open(file, 'w') as fp:
            yaml.dump(d, fp)

    def values(self) -> typing.ValuesView[typing.Any]:
        r"""Returns parameter values.

        """
        return self.__dict__.values()

    def __getattribute__(self, name) -> typing.Any:
        if not name == '__dict__' and name in self.__dict__:
            p = self.__dict__[name]
            return p.value
        return object.__getattribute__(self, name)

    def __repr__(self):  # pragma: no cover
        return str(self.to_dict())

    def __setattr__(self, name: str, value: typing.Any):
        p = self.__dict__[name]
        p.set_value(value)

    def __str__(self):  # pragma: no cover
        table = [
            [
                'Name', 'Value', 'Default', 'Choices',
                'Description', 'Version',
            ]
        ]
        for name, p in self.items():
            table.append(
                [
                    name, p.value, p.default, p.choices,
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

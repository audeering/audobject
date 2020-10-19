import inspect
import os
import typing
import warnings

import oyaml as yaml

import audeer

from audobject.core import define
from audobject.core import utils


class Object:
    r"""Base class for objects that can be serialized to YAML.

    Example:

    >>> class Foo(Object):
    ...    def __init__(self, bar: str):
    ...        self.bar = bar
    >>> foo = Foo('hello object!')
    >>> print(foo)
    $audobject.core.object.Foo:
      bar: hello object!

    """
    @property
    def arguments(self) -> typing.Dict[str, typing.Any]:
        r"""Returns arguments that are serialized.

        Returns:
            Dictionary of arguments and their values.

        Raises:
            RuntimeError: if arguments are found that are not assigned to
                attributes of the same name

        """
        signature = inspect.signature(self.__init__)
        # if 'kwargs' are allowed, check all members
        # otherwise only arguments from __init__
        if 'kwargs' in signature.parameters:
            names = self.__dict__
        else:
            names = [p.name for p in signature.parameters.values()]
        # remove hidden variables
        hidden = list(self.hidden_arguments)
        names = [
            name for name in names if (
                (name != 'self')
                and (not name.startswith('_'))
                and (name not in hidden)
            )
        ]
        # check for missing attributes
        missing = []
        for name in names:
            if name not in self.__dict__:
                missing.append(name)
        if len(missing) > 0:
            raise RuntimeError(f'Arguments(s) {missing} not '
                               f'assigned to attribute(s) '
                               f'of same name(s).')
        return {
            name: self.__dict__[name] for name in names if (
                (name in self.__dict__)
            )
        }

    @property
    def hidden_arguments(self) -> typing.List[str]:
        r"""Returns hidden arguments.

        Returns:
            List with names of hidden arguments.

        """
        if define.HIDDEN_ATTRIBUTES in self.__dict__:
            names = list(self.__dict__[define.HIDDEN_ATTRIBUTES])
        else:
            names = []
        return names

    @property
    def id(self) -> str:
        r"""Object identifier.

        The ID of an object ID is created from its non-hidden arguments.

        Example:

        >>> class Foo(Object):
        ...    def __init__(self, bar: str):
        ...        self.bar = bar
        >>> foo1 = Foo('I am unique!')
        >>> print(foo1.id)
        893df240-babe-d796-cdf1-c436171b7a96
        >>> foo2 = Foo('I am different!')
        >>> print(foo2.id)
        9303f2a5-bfc9-e5ff-0ffa-a9846e2d2190
        >>> foo3 = Foo('I am unique!')
        >>> print(foo1.id == foo3.id)
        True

        """
        string = self.to_yaml_s(include_version=False)
        return audeer.uid(from_string=string)

    @staticmethod
    def from_dict(
            d: typing.Dict[str, typing.Any],
            **kwargs,
    ) -> 'Object':
        r"""Create object from dictionary.

        Args:
            d: dictionary with variables
            kwargs: additional variables

        Returns:
            object

        Raises:
            RuntimeError: if a mandatory argument of the object
                is missing in the dictionary

        """
        name = next(iter(d))
        cls, version, installed_version = utils.get_class(name)
        params = {}
        for key, value in d[name].items():
            params[key] = Object._decode_value(value, **kwargs)
        for key, value in kwargs.items():
            params[key] = value
        return utils.get_object(cls, version, installed_version, params)

    @staticmethod
    def from_yaml(
            path_or_stream: typing.Union[str, typing.IO],
            **kwargs,
    ) -> 'Object':
        r"""Create object from YAML file.

        Args:
            path_or_stream: file path or stream
            kwargs: additional variables

        Returns:
            object

        """
        if isinstance(path_or_stream, str):
            with open(path_or_stream, 'r') as fp:
                return Object.from_yaml(fp)
        return Object.from_dict(
            yaml.load(path_or_stream, yaml.Loader),
            **kwargs,
        )

    @staticmethod
    def from_yaml_s(
            yaml_string: str,
            **kwargs,
    ) -> 'Object':
        r"""Create object from YAML string.

        Args:
            yaml_string: YAML string
            kwargs: additional variables

        Returns:
            object

        """
        return Object.from_dict(
            yaml.load(yaml_string, yaml.Loader),
            **kwargs,
        )

    @property
    def resolvers(self):
        r"""Return resolvers.

        Returns:
            Dictionary with resolvers.

        """
        if hasattr(self, define.CUSTOM_VALUE_RESOLVERS):
            return self.__dict__[define.CUSTOM_VALUE_RESOLVERS]
        return {}

    def to_dict(
            self,
            *,
            include_version: bool = True,
    ) -> typing.Dict[str, typing.Any]:
        r"""Converts object to a dictionary.

        Args:
            include_version: add version to class name

        Returns:
            dictionary with parameters

        """
        name = f'{define.OBJECT_TAG}' \
               f'{self.__class__.__module__}.' \
               f'{self.__class__.__name__}'
        if include_version:
            version = utils.get_version(self.__class__.__module__)
            if version is not None:
                name += f'{define.VERSION_TAG}{version}'
            else:
                warnings.warn(
                    f"Could not determine a version for "
                    f"module '{self.__class__.__module__}'.",
                    RuntimeWarning,
                )
        d = {}
        for key, value in self.arguments.items():
            d[key] = self._encode_variable(key, value, include_version)
        return {name: d}

    def to_yaml(
            self,
            path_or_stream: typing.Union[str, typing.IO],
            *,
            include_version: bool = True,
    ):
        r"""Save object to YAML file.

        Args:
            path_or_stream: file path or stream
            include_version: add version to class name

        """
        if isinstance(path_or_stream, str):
            path_or_stream = audeer.safe_path(path_or_stream)
            root = os.path.dirname(path_or_stream)
            audeer.mkdir(root)
            with open(path_or_stream, 'w') as fp:
                return self.to_yaml(fp, include_version=include_version)
        else:
            return yaml.dump(
                self.to_dict(include_version=include_version),
                path_or_stream,
            )

    def to_yaml_s(
            self,
            *,
            include_version: bool = True,
    ) -> str:
        r"""Convert object to YAML string.

        Args:
            include_version: add version to class name

        Returns:
            YAML string

        """
        return yaml.dump(self.to_dict(include_version=include_version))

    @staticmethod
    def _decode_value(
            value_to_decode: typing.Any,
            **kwargs,
    ) -> typing.Any:
        r"""Decode value."""
        if value_to_decode:  # not empty
            if isinstance(value_to_decode, list):
                return [
                    Object._decode_value(v, **kwargs) for v in value_to_decode
                ]
            elif isinstance(value_to_decode, dict):
                name = next(iter(value_to_decode))
                if isinstance(name, Object) or utils.is_class(name):
                    return Object.from_dict(value_to_decode, **kwargs)
                else:
                    return {
                        k: Object._decode_value(v, **kwargs) for k, v in
                        value_to_decode.items()
                    }
        return value_to_decode

    def _encode_variable(
            self,
            name: str,
            value: typing.Any,
            include_version: bool,
    ):
        r"""Encode a value by first looking for a custom resolver,
        otherwise switch to default encoder."""
        if name in self.resolvers:
            value = self.resolvers[name].encode(value)
        return Object._encode_value(value, include_version)

    @staticmethod
    def _encode_value(
            value: typing.Any,
            include_version: bool,
    ):
        r"""Default value encoder."""
        if value is None:
            return None
        elif isinstance(value, Object) or utils.is_class(value):
            return value.to_dict(include_version=include_version)
        elif isinstance(value, define.DEFAULT_VALUE_TYPES):
            return value
        elif isinstance(value, list):
            return [
                Object._encode_value(
                    item, include_version
                ) for item in value
            ]
        elif isinstance(value, dict):
            return {
                Object._encode_value(key, include_version):
                    Object._encode_value(val, include_version)
                for key, val in value.items()
            }
        else:
            warnings.warn(
                f"No default encoding exists for type '{type(value)}'. "
                f"Consider to register a custom resolver.",
                RuntimeWarning,
            )
            return value

    def __eq__(self, other: 'Object') -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return str(self.to_dict(include_version=False))

    def __str__(self) -> str:
        return self.to_yaml_s(include_version=False)

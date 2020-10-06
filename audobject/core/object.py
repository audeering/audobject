import os
import typing
import warnings

import oyaml as yaml

import audeer

from audobject.core import define
from audobject.core import utils


class Object:
    r"""Base class for objects we want to serialize to YAML.

    Objects can be reconstructed from YAML if the following rules apply:

    * Every parameter of the constructor is assigned to a class variables
      with the name of the parameter:

      .. code-block:: python

          class Foo(audobject.Object):
              def __init__(self, foo: str):
                  self.foo = foo
                  # self.bar = foo  # bad, name of parameter is 'foo'

    * Other class variables are private,
      i.e. start with a ``_`` (use properties to expose them):

      .. code-block:: python

          class Foo(audobject.Object):
              def __init__(self, foo: str):
                  self.foo = foo
                  self._bar = foo + foo
                  # self.bar = foo + foo  # bad, 'bar' is not a parameter

              @property
              def bar(self):
                  return self._bar

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
    def id(self) -> str:
        r"""Object identifier.

        .. note:: Objects with same properties have the same ID.

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
    def from_dict(d: dict) -> 'Object':
        r"""Create object from dictionary.

        Args:
            d: dictionary with parameters

        Returns:
            object

        Raises:
            RuntimeError: if a mandatory parameter of the object
                is missing in the dictionary

        """
        name = next(iter(d))
        cls, version, installed_version = utils.get_class(name)
        params = {}
        for key, value in d[name].items():
            params[key] = Object._decode_value(value)
        return utils.get_object(cls, version, installed_version, params)

    @staticmethod
    def from_yaml(
            path_or_stream: typing.Union[str, typing.IO],
    ) -> 'Object':
        r"""Create object from YAML file.

        Args:
            path_or_stream: file path or stream

        Returns:
            object

        """
        if isinstance(path_or_stream, str):
            with open(path_or_stream, 'r') as fp:
                return Object.from_yaml(fp)
        return Object.from_dict(yaml.load(path_or_stream, yaml.Loader))

    @staticmethod
    def from_yaml_s(string: str) -> 'Object':
        r"""Create object from YAML string.

        Args:
            string: YAML string

        Returns:
            object

        """
        return Object.from_dict(yaml.load(string, yaml.Loader))

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
        return {
            name: {
                key: self._encode_value(
                    key, value, include_version
                ) for key, value in self.__dict__.items()
                if not key.startswith('_')
            }
        }

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

    def _encode_value(
            self,
            name: str,
            value: typing.Any,
            include_version: bool,
    ):
        r"""Encode a value by first looking for a custom resolver,
        otherwise switch to default encoder."""
        if hasattr(self, define.CUSTOM_VALUE_RESOLVERS):
            resolvers = self.__dict__[define.CUSTOM_VALUE_RESOLVERS]
            if name in resolvers:
                value = resolvers[name].encode(value)
        return Object._encode_value_default(value, include_version)

    @staticmethod
    def _encode_value_default(
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
                Object._encode_value_default(
                    item, include_version
                ) for item in value
            ]
        elif isinstance(value, dict):
            return {
                Object._encode_value_default(key, include_version):
                    Object._encode_value_default(val, include_version)
                for key, val in value.items()
            }
        else:
            warnings.warn(
                f"No default encoding exists for type '{type(value)}'. "
                f"Consider to register a custom resolver.",
                RuntimeWarning,
            )
            return value

    @staticmethod
    def _decode_value(value: typing.Any) -> typing.Any:
        r"""Default value decoder."""
        if isinstance(value, list):
            return [Object._decode_value(v) for v in value]
        elif isinstance(value, dict):
            name = next(iter(value))
            if isinstance(name, Object) or utils.is_class(name):
                return Object.from_dict(value)
            else:
                return {
                    k: Object._decode_value(v) for k, v in
                    value.items()
                }
        else:
            return value

    def __eq__(self, other: 'Object') -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return str(self.to_dict(include_version=False))

    def __str__(self) -> str:
        return self.to_yaml_s(include_version=False)

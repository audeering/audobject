import importlib
import os
import typing
import warnings

import oyaml as yaml


import audeer


OBJECT_TAG = '$'


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

    * If the type of a variable is not one of
      ``(None, Object, str, int, float, bool, list, dict)``,
      a special resolver must be provided:

      .. code-block:: python

          class TupleResolver(audobject.ValueResolver):

              def encode(self, value: tuple) -> list:
                  return list(value)

              def decode(self, value: list) -> tuple:
                  return tuple(value)

          class Foo(audobject.Object):
              def __init__(self, foo: tuple):
                  self._value_resolver['foo'] = TupleResolver()
                  self.foo = foo

      Or alternatively:

      .. code-block:: python

        class Foo(audobject.Object):

            def __init__(self, foo: tuple):
                self._value_resolver['foo'] = (
                    lambda x: list(x),
                    lambda x: tuple(x),
                )
                self.foo = foo

    Example:

    >>> class Foo(Object):
    ...    def __init__(self, bar: str):
    ...        self.bar = bar
    >>> foo = Foo('hello object!')
    >>> print(foo)
    $audobject.core.api.Foo:
      bar: hello object!

    """
    _value_resolver = {}

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
        35b222ae-4086-05e6-ac8b-b86f65df22ff
        >>> foo2 = Foo('I am different!')
        >>> print(foo2.id)
        5ef54bc6-8beb-ff4b-b256-b80b15db5753
        >>> foo3 = Foo('I am unique!')
        >>> print(foo1.id == foo3.id)
        True

        """
        return audeer.uid(from_string=str(self))

    @staticmethod
    def from_dict(d: dict) -> 'Object':
        r"""Create object from dictionary.

        Args:
            d: dictionary with parameters

        Returns:
            object

        """
        name = next(iter(d))
        cls = Object._get_class(name)
        params = {}
        for key, value in d[name].items():
            params[key] = Object._decode_value(cls, key, value)
        return cls(**params)

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

    def to_dict(self) -> dict:
        r"""Converts object to a dictionary.

        Returns:
            dictionary with parameters

        """
        name = f'{OBJECT_TAG}' \
               f'{self.__class__.__module__}.' \
               f'{self.__class__.__name__}'
        return {
            name: {
                key: self._encode_value(key, value) for key, value in
                self.__dict__.items() if not key.startswith('_')
            }
        }

    def to_yaml(self, path_or_stream: typing.Union[str, typing.IO]):
        r"""Save object to YAML file.

        Args:
            path_or_stream: file path or stream

        """
        if isinstance(path_or_stream, str):
            path_or_stream = audeer.safe_path(path_or_stream)
            root = os.path.dirname(path_or_stream)
            audeer.mkdir(root)
            with open(path_or_stream, 'w') as fp:
                return self.to_yaml(fp)
        return yaml.dump(self.to_dict(), path_or_stream)

    def to_yaml_s(self) -> str:
        r"""Convert object to YAML string.

        Returns:
            YAML string

        """
        return yaml.dump(self.to_dict())

    def _encode_value(self, name: str, value: typing.Any):
        r"""Encode a value by first looking for a custom resolver,
        otherwise switch to default encoder."""
        if name in self._value_resolver:
            if isinstance(self._value_resolver[name], ValueResolver):
                value = self._value_resolver[name].encode(value)
            else:
                value = self._value_resolver[name][0](value)
        return Object._encode_value_default(value)

    @staticmethod
    def _encode_value_default(value: typing.Any):
        r"""Default value encoder."""
        if value is None:
            return None
        elif Object._is_class(value):
            return value.to_dict()
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, list):
            return [
                Object._encode_value_default(item) for item in value
            ]
        elif isinstance(value, dict):
            return {
                Object._encode_value_default(key):
                    Object._encode_value_default(val) for key, val
                in value.items()
            }
        else:
            warnings.warn(
                f"No encoding exists for type '{type(value)}'. "
                f"Calling 'repr()' to encode the value. "
                f"Consider to register a custom resolver.",
                RuntimeWarning,
            )
            return repr(value)

    @staticmethod
    def _decode_value(
            cls: 'Object',
            name: str,
            value: typing.Any
    ) -> typing.Any:
        r"""Decode a value by first looking for a custom resolver,
        otherwise switch to default encoder."""
        if name in cls._value_resolver:
            if isinstance(cls._value_resolver[name], ValueResolver):
                value = cls._value_resolver[name].decode(value)
            else:
                value = cls._value_resolver[name][1](value)
        return Object._decode_value_default(value)

    @staticmethod
    def _decode_value_default(value: typing.Any) -> typing.Any:
        r"""Default value decoder."""
        if isinstance(value, list):
            return [Object._decode_value_default(v) for v in value]
        elif isinstance(value, dict):
            name = next(iter(value))
            if Object._is_class(name):
                return Object.from_dict(value)
            else:
                return {
                    k: Object._decode_value_default(v) for k, v in
                    value.items()
                }
        else:
            return value

    @staticmethod
    def _get_class(key: str):
        r"""Load class module."""
        if key.startswith(OBJECT_TAG):
            key = key[len(OBJECT_TAG):]
        module_name, class_name = Object._split_key(key)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    @staticmethod
    def _is_class(value: typing.Any):
        r"""Check if value is a class."""
        if isinstance(value, Object):
            return True
        elif isinstance(value, str):
            if value.startswith(OBJECT_TAG):
                return True
            # only for backward compatibility with `auglib` and `audbenchmark`
            if value.startswith('auglib.core.') or \
                    value.startswith('audbenchmark.core.'):
                return True  # pragma: no cover
        return False

    @staticmethod
    def _split_key(key: str) -> [str, str]:
        r"""Split value key in module and class name."""
        tokens = key.split('.')
        module_name = '.'.join(tokens[:-1])
        class_name = tokens[-1]
        return module_name, class_name

    def __eq__(self, other: 'Object') -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return str(self.to_dict())

    def __str__(self) -> str:
        return self.to_yaml_s()


DefaultValueType = typing.Union[
    None, Object, str, int, float, bool, list, dict,
]


class ValueResolver:
    r"""Abstract resolver class.

    Implement for parameters that are not one of
    ``(None, Object, str, int, float, bool, list, dict)``.

    """
    def encode(self, value: typing.Any) -> DefaultValueType:
        r"""Encode value.

        The type of the returned value must be one of
        ``(None, Object, str, int, float, bool, list, dict)``.

        Args:
            value: value to encode

        Returns:
            encoded value

        """
        raise NotImplementedError  # pragma: no cover

    def decode(self, value: DefaultValueType) -> typing.Any:
        r"""Decode value.

        Takes the encoded value and converts it back to its original type.

        Args:
            value: value to decode

        Returns:
            decoded value

        """
        raise NotImplementedError  # pragma: no cover


class TupleResolver(ValueResolver):
    r"""Tuple resolver."""

    def encode(self, value: tuple) -> list:
        r"""Encodes ``tuple`` as ``list``.

        Args:
            value: tuple

        Returns:
            list

        """
        return list(value)

    def decode(self, value: list) -> tuple:
        r"""Decodes ``list`` as ``tuple``.

        Args:
            value: list

        Returns:
            tuple

        """
        return tuple(value)

import importlib
import inspect
import os
import typing
import warnings

import oyaml as yaml

import audeer

from audobject.core.config import config
from audobject.core import define


OBJECT_TAG = '$'
VERSION_TAG = '=='


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
        cls, version, installed_version = Object._get_class(name)
        params = {}
        for key, value in d[name].items():
            params[key] = Object._decode_value(cls, key, value)
        return Object._get_object(cls, version, installed_version, params)

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
    ) -> dict:
        r"""Converts object to a dictionary.

        Args:
            include_version: add version to class name

        Returns:
            dictionary with parameters

        """
        name = f'{OBJECT_TAG}' \
               f'{self.__class__.__module__}.' \
               f'{self.__class__.__name__}'
        if include_version:
            version = Object._get_version(self.__class__.__module__)
            if version is not None:
                name += f'{VERSION_TAG}{version}'
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
            self, name: str,
            value: typing.Any,
            include_version: bool,
    ):
        r"""Encode a value by first looking for a custom resolver,
        otherwise switch to default encoder."""
        if name in self._value_resolver:
            if isinstance(self._value_resolver[name], ValueResolver):
                value = self._value_resolver[name].encode(value)
            else:
                value = self._value_resolver[name][0](value)
        return Object._encode_value_default(value, include_version)

    @staticmethod
    def _encode_value_default(
            value: typing.Any,
            include_version: bool,
    ):
        r"""Default value encoder."""
        if value is None:
            return None
        elif Object._is_class(value):
            return value.to_dict(include_version=include_version)
        elif isinstance(value, (str, int, float, bool)):
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
    def _get_class(key: str) -> (type, str, str):
        r"""Load class module."""
        if key.startswith(OBJECT_TAG):
            key = key[len(OBJECT_TAG):]
        module_name, class_name, version = Object._split_key(key)
        installed_version = Object._get_version(module_name)
        module = importlib.import_module(module_name)
        return getattr(module, class_name), version, installed_version

    @staticmethod
    def _get_object(
        cls: type,
        version: str,
        installed_version: str,
        params: dict,
    ) -> 'Object':
        r"""Create object from parameters."""
        signature = inspect.signature(cls.__init__)
        supports_kwargs = 'kwargs' in signature.parameters

        # check for missing mandatory parameters
        required_params = set([
            p.name for p in signature.parameters.values()
            if p.default == inspect.Parameter.empty and p.name not in [
                'self', 'kwargs',
            ]
        ])
        missing_required_params = list(required_params - set(params))
        if len(missing_required_params) > 0:
            raise RuntimeError(
                f"Missing mandatory parameter(s) "
                f"{missing_required_params} "
                f"while instantiating '{cls}' from "
                f"version '{version}' when using "
                f"version '{installed_version}'."
            )

        # check for missing optional parameters
        optional_params = set([
            p.name for p in signature.parameters.values()
            if p.default != inspect.Parameter.empty and p.name not in [
                'self', 'kwargs',
            ]
        ])
        missing_optional_params = list(optional_params - set(params))
        if len(missing_optional_params) > 0:
            if config.SIGNATURE_MISMATCH_WARN_LEVEL > \
                    define.SignatureMismatchWarnLevel.STANDARD:
                warnings.warn(
                    f"Missing optional parameter(s) "
                    f"{missing_optional_params} "
                    f"while instantiating '{cls}' from "
                    f"version '{version}' when using "
                    f"version '{installed_version}'.",
                    RuntimeWarning,
                )

        # unless kwargs are supported check for additional parameters
        if not supports_kwargs:
            supported_params = set([
                p.name for p in signature.parameters.values()
                if p.name not in ['self', 'kwargs']
            ])
            additional_params = list(set(params) - supported_params)
            if len(additional_params):
                if config.SIGNATURE_MISMATCH_WARN_LEVEL > \
                        define.SignatureMismatchWarnLevel.SILENT:
                    warnings.warn(
                        f"Ignoring parameter(s) "
                        f"{additional_params} "
                        f"while instantiating '{cls}' from "
                        f"version '{version}' when using "
                        f"version '{installed_version}'.",
                        RuntimeWarning,
                    )
                params = {
                    key: value for key, value in params.items()
                    if key in supported_params
                }

        return cls(**params)

    @staticmethod
    def _get_version(module_name: str) -> typing.Optional[str]:
        module = importlib.import_module(module_name.split('.')[0])
        if '__version__' in module.__dict__:
            return module.__version__
        else:
            return None

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
    def _split_key(key: str) -> [str, str, typing.Optional[str]]:
        r"""Split value key in module, class and version."""
        version = None
        if VERSION_TAG in key:
            key, version = key.split(VERSION_TAG)
        tokens = key.split('.')
        module_name = '.'.join(tokens[:-1])
        class_name = tokens[-1]
        return module_name, class_name, version

    def __eq__(self, other: 'Object') -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return str(self.to_dict(include_version=False))

    def __str__(self) -> str:
        return self.to_yaml_s(include_version=False)


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

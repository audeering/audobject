import os
import typing
import warnings

import oyaml as yaml

from audobject.core.object import Object
import audobject.core.utils as utils


kwargs_deprecation_warning = (
    "The use of **kwargs is deprecated "
    "and will be removed with version 1.0.0. "
    "Use 'override_args' instead."
)


def from_dict(
        d: typing.Dict[str, typing.Any],
        root: str = None,
        *,
        override_args: typing.Dict[str, typing.Any] = None,
        **kwargs,
) -> 'Object':
    r"""Create object from dictionary.

    Args:
        d: dictionary with arguments
        root: if dictionary was read from a file, set to source directory
        override_args: override arguments in ``d`` or
            default values of hidden arguments

    Returns:
        object

    Raises:
        RuntimeError: if a mandatory argument of the object
            is missing in the dictionary ``d``

    """
    override_args = override_args or {}

    if kwargs:
        warnings.warn(
            kwargs_deprecation_warning,
            category=UserWarning,
            stacklevel=2,
        )
        for key, value in kwargs.items():
            override_args[key] = value

    name = next(iter(d))
    cls, version, installed_version = utils.get_class(name)
    params = {}
    for key, value in d[name].items():
        params[key] = _decode_value(value, override_args)
    return utils.get_object(
        cls,
        version,
        installed_version,
        params,
        root,
        override_args,
    )


def from_yaml(
        path_or_stream: typing.Union[str, typing.IO],
        *,
        override_args: typing.Dict[str, typing.Any] = None,
        **kwargs,
) -> 'Object':
    r"""Create object from YAML file.

    Args:
        path_or_stream: file path or stream
        override_args: override arguments in the YAML file or
            default values of hidden arguments

    Returns:
        object

    """
    override_args = override_args or {}

    if kwargs:
        warnings.warn(
            kwargs_deprecation_warning,
            category=UserWarning,
            stacklevel=2,
        )
        for key, value in kwargs.items():
            override_args[key] = value

    if isinstance(path_or_stream, str):
        with open(path_or_stream, 'r') as fp:
            return from_yaml(fp, override_args=override_args)
    return from_dict(
        yaml.load(path_or_stream, yaml.Loader),
        root=os.path.dirname(path_or_stream.name),
        override_args=override_args,
    )


def from_yaml_s(
        yaml_string: str,
        *,
        override_args: typing.Dict[str, typing.Any] = None,
        **kwargs,
) -> 'Object':
    r"""Create object from YAML string.

    Args:
        yaml_string: YAML string
        override_args: override arguments in the YAML string or
            default values of hidden arguments

    Returns:
        object

    """
    override_args = override_args or {}

    if kwargs:
        warnings.warn(
            kwargs_deprecation_warning,
            category=UserWarning,
            stacklevel=2,
        )
        for key, value in kwargs.items():
            override_args[key] = value

    return from_dict(
        yaml.load(yaml_string, yaml.Loader),
        override_args=override_args,
    )


def _decode_value(
        value_to_decode: typing.Any,
        override_args: typing.Dict[str, typing.Any],
) -> typing.Any:
    r"""Decode value."""
    if value_to_decode:  # not empty
        if isinstance(value_to_decode, list):
            return [
                _decode_value(v, override_args) for v in value_to_decode
            ]
        elif isinstance(value_to_decode, dict):
            name = next(iter(value_to_decode))
            if isinstance(name, Object) or utils.is_class(name):
                return from_dict(value_to_decode, override_args=override_args)
            else:
                return {
                    k: _decode_value(v, override_args) for k, v in
                    value_to_decode.items()
                }
    return value_to_decode

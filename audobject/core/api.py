import os
import typing

import oyaml as yaml

from audobject.core.object import Object
import audobject.core.utils as utils


def _decode_value(
        value_to_decode: typing.Any,
        **kwargs,
) -> typing.Any:
    r"""Decode value."""
    if value_to_decode:  # not empty
        if isinstance(value_to_decode, list):
            return [
                _decode_value(v, **kwargs) for v in value_to_decode
            ]
        elif isinstance(value_to_decode, dict):
            name = next(iter(value_to_decode))
            if isinstance(name, Object) or utils.is_class(name):
                return load_from_dict(value_to_decode, **kwargs)
            else:
                return {
                    k: _decode_value(v, **kwargs) for k, v in
                    value_to_decode.items()
                }
    return value_to_decode


def load_from_dict(
        d: typing.Dict[str, typing.Any],
        root: str = None,
        **kwargs,
) -> 'Object':
    r"""Create object from dictionary.

    Args:
        d: dictionary with variables
        root: if dictionary was read from a file, set to source directory
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
        params[key] = _decode_value(value, **kwargs)
    return utils.get_object(
        cls,
        version,
        installed_version,
        params,
        root,
        **kwargs,
    )


def load_from_yaml(
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
            return load_from_yaml(fp, **kwargs)
    return load_from_dict(
        yaml.load(path_or_stream, yaml.Loader),
        root=os.path.dirname(path_or_stream.name),
        **kwargs,
    )


def load_from_yaml_s(
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
    return load_from_dict(
        yaml.load(yaml_string, yaml.Loader),
        **kwargs,
    )
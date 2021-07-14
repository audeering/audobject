import importlib
import inspect
import typing
import warnings

from audobject.core.config import config
from audobject.core import define


def get_class(key: str) -> (type, str, str):
    r"""Load class module."""
    if key.startswith(define.OBJECT_TAG):
        key = key[len(define.OBJECT_TAG):]
    module_name, class_name, version = split_key(key)
    installed_version = get_version(module_name)
    module = importlib.import_module(module_name)
    return getattr(module, class_name), version, installed_version


def get_object(
        cls: type,
        version: str,
        installed_version: str,
        params: dict,
        root: typing.Optional[str],
        **kwargs,
) -> typing.Any:
    r"""Create object from arguments."""
    signature = inspect.signature(cls.__init__)
    supports_kwargs = 'kwargs' in signature.parameters
    supported_params = set([
        p.name for p in signature.parameters.values()
        if p.name not in ['self', 'kwargs']
    ])

    # check for missing mandatory arguments
    required_params = set([
        p.name for p in signature.parameters.values()
        if p.default == inspect.Parameter.empty and p.name not in [
            'self', 'args', 'kwargs',
        ]
    ])
    missing_required_params = list(required_params - set(params))
    if len(missing_required_params) > 0:
        raise RuntimeError(
            f"Missing mandatory arguments "
            f"{missing_required_params} "
            f"while instantiating {cls} from "
            f"version '{version}' when using "
            f"version '{installed_version}'."
        )

    # check for missing optional arguments
    optional_params = set([
        p.name for p in signature.parameters.values()
        if p.default != inspect.Parameter.empty and p.name not in [
            'self', 'args', 'kwargs',
        ]
    ])
    missing_optional_params = list(optional_params - set(params))
    if len(missing_optional_params) > 0:
        if config.SIGNATURE_MISMATCH_WARN_LEVEL > \
                define.SignatureMismatchWarnLevel.STANDARD:
            warnings.warn(
                f"Missing optional arguments "
                f"{missing_optional_params} "
                f"while instantiating {cls} from "
                f"version '{version}' when using "
                f"version '{installed_version}'.",
                RuntimeWarning,
            )

    # unless kwargs are supported check for additional arguments
    if not supports_kwargs:
        additional_params = list(set(params) - supported_params)
        if len(additional_params):
            if config.SIGNATURE_MISMATCH_WARN_LEVEL > \
                    define.SignatureMismatchWarnLevel.SILENT:
                warnings.warn(
                    f"Ignoring arguments "
                    f"{additional_params} "
                    f"while instantiating {cls} from "
                    f"version '{version}' when using "
                    f"version '{installed_version}'.",
                    RuntimeWarning,
                )
            params = {
                key: value for key, value in params.items()
                if key in supported_params
            }

    # select supported params from kwargs
    for key, value in kwargs.items():
        if key in supported_params:
            params[key] = value

    # If function has init decorator, add stream to parameters.
    # The additional parameter will be popped by the decorator
    # before the object is created.
    # If the class does not have a decorator
    # a TypeError will be raised since we call
    # the class with an unexpected argument.
    # Unfortunately, there is no straight-forward way
    # to check if a method of a class has a decorator
    # so we have to use a try-except block
    try:
        params[define.ROOT_ATTRIBUTE] = root
        return cls(**params)
    except TypeError:
        params.pop(define.ROOT_ATTRIBUTE)
        return cls(**params)


def get_version(module_name: str) -> typing.Optional[str]:
    module = importlib.import_module(module_name.split('.')[0])
    if '__version__' in module.__dict__:
        return module.__version__
    else:
        return None


def is_class(value: typing.Any):
    r"""Check if value is a class."""
    if isinstance(value, str):
        if value.startswith(define.OBJECT_TAG):
            return True
        # only for backward compatibility with `auglib` and `audbenchmark`
        if value.startswith('auglib.core.') or \
                value.startswith('audbenchmark.core.'):
            return True  # pragma: no cover
    return False


def split_key(key: str) -> [str, str, typing.Optional[str]]:
    r"""Split value key in module, class and version."""
    version = None
    if define.VERSION_TAG in key:
        key, version = key.split(define.VERSION_TAG)
    tokens = key.split('.')
    module_name = '.'.join(tokens[:-1])
    class_name = tokens[-1]
    return module_name, class_name, version

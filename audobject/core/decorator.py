import functools
import inspect
import typing
import warnings

import audeer

from audobject.core import define
from audobject.core.resolver import ValueResolver


@audeer.deprecated_keyword_argument(
    deprecated_argument='ignore_vars',
    removal_version='0.5.0',
    new_argument='hide',
)
def init_decorator(
        hide: typing.Sequence[str] = None,
        resolvers: typing.Dict[str, typing.Type[ValueResolver]] = None,
):
    r"""Decorator for ``__init__`` function of :class:`audobject.Object`.

    Arguments listed in ``hidden`` are not serialized to YAML.

    If a dictionary of :class:`audobject.ValueResolver` is passed,
    matching attributes will be encoded / decoded
    using the according :class:`audobject.ValueResolver`.

    Args:
        hide: hidden attributes
        resolvers: dictionary with resolvers

    Raises:
        RuntimeError: if arguments are not assigned to attributes of same name

    """
    def decorator(func):

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):

            if resolvers is not None:
                setattr(self, define.CUSTOM_VALUE_RESOLVERS, {})
                for name, resolver in resolvers.items():
                    resolver_obj = resolver()
                    self.__dict__[define.CUSTOM_VALUE_RESOLVERS][name] = \
                        resolver_obj
                    if name in kwargs and isinstance(
                            kwargs[name], resolver_obj.encode_type()
                    ):
                        kwargs[name] = resolver_obj.decode(kwargs[name])

            if hide is not None:

                signature = inspect.signature(func)
                required = set([
                    p.name for p in signature.parameters.values()
                    if p.default == inspect.Parameter.empty and p.name not in [
                        'self', 'args', 'kwargs',
                    ]
                ])

                hidden = []
                if hide is not None:
                    for var in hide:
                        hidden.append(var)

                invalid = []
                for var in hidden:
                    if var in required:
                        invalid.append(var)
                if len(invalid) > 0:
                    raise RuntimeError(
                        f'Cannot hide arguments '
                        f'{invalid} '
                        f'of '
                        f'{self.__class__} '
                        f'as they do not have default values.'
                    )

                setattr(self, define.HIDDEN_ATTRIBUTES, hidden)

            func(self, *args, **kwargs)

        return wrapper

    return decorator

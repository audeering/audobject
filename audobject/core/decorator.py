import functools
import inspect
import typing

import audeer

from audobject.core import define
from audobject.core.resolver import ValueResolver


@audeer.deprecated_keyword_argument(
    deprecated_argument='ignore_vars',
    removal_version='0.5.0',
    new_argument='hide',
)
def init_decorator(
        *,
        borrow: typing.Dict[str, str] = None,
        hide: typing.Sequence[str] = None,
        resolvers: typing.Dict[str, typing.Type[ValueResolver]] = None,
):
    r"""Decorator for ``__init__`` function of :class:`audobject.Object`.

    If your class expects an argument ``x`` which is passed on as an argument
    to a class ``C`` or to a dictionary with key ``x`` and stored under
    ``self.c``, you can borrow the argument from ``c`` by setting ``borrow[
    'x'] = 'c'``. This will store ``x`` in the YAML representation, even so
    your class does have an actual corresponding attribute ``self.x``.

    Arguments listed in ``hidden`` are not serialized to YAML.
    Note that objects you borrow attributes from, are also treated as
    hidden arguments.

    If a dictionary of :class:`audobject.ValueResolver` is passed,
    matching attributes will be encoded / decoded
    using the according :class:`audobject.ValueResolver`.

    Args:
        borrow: borrowed attributes
        hide: hidden attributes
        resolvers: dictionary with resolvers

    Raises:
        RuntimeError: if arguments are not assigned to attributes of same name

    """
    def decorator(func):

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):

            if resolvers is not None:

                if not hasattr(self, define.CUSTOM_VALUE_RESOLVERS):
                    setattr(self, define.CUSTOM_VALUE_RESOLVERS, {})

                for name, resolver in resolvers.items():
                    resolver_obj = resolver()
                    # let resolver know if we read from a stream
                    if define.ROOT_ATTRIBUTE in kwargs:
                        resolver_obj.__dict__[define.ROOT_ATTRIBUTE] = \
                            kwargs[define.ROOT_ATTRIBUTE]
                    self.__dict__[define.CUSTOM_VALUE_RESOLVERS][name] = \
                        resolver_obj
                    if name in kwargs and isinstance(
                            kwargs[name], resolver_obj.encode_type()
                    ):
                        kwargs[name] = resolver_obj.decode(kwargs[name])

            if borrow is not None:

                if not hasattr(self, define.BORROWED_ATTRIBUTES):
                    setattr(self, define.BORROWED_ATTRIBUTES, {})

                for key, value in borrow.items():
                    self.__dict__[define.BORROWED_ATTRIBUTES][key] = value

            if hide is not None:

                signature = inspect.signature(func)
                required = set([
                    p.name for p in signature.parameters.values()
                    if p.default == inspect.Parameter.empty and p.name not in [
                        'self', 'args', 'kwargs',
                    ]
                ])

                invalid = []
                for var in hide:
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

                if not hasattr(self, define.HIDDEN_ATTRIBUTES):
                    setattr(self, define.HIDDEN_ATTRIBUTES, [])
                self.__dict__[define.HIDDEN_ATTRIBUTES] += hide

            # if stream was set we can pop it now
            if define.ROOT_ATTRIBUTE in kwargs:
                kwargs.pop(define.ROOT_ATTRIBUTE)

            func(self, *args, **kwargs)

        return wrapper

    return decorator

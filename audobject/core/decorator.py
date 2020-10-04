import functools
import typing

from audobject.core import define
from audobject.core.resolver import ValueResolver


def init_object_decorator(
        resolvers: typing.Dict[str, typing.Type[ValueResolver]],
):
    r"""Decorator to add value resolvers.

    Takes a dictionary with variable names as keys and
    :class:`audobject.ValueResolver` as values.

    Args:
        resolvers: dictionary with resolvers

    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            setattr(self, define.CUSTOM_VALUE_RESOLVERS, {})
            for name, resolver in resolvers.items():
                resolver_obj = resolver()
                self.__dict__[define.CUSTOM_VALUE_RESOLVERS][name] = \
                    resolver_obj
                if name in kwargs and isinstance(
                        kwargs[name], resolver_obj.encode_type()
                ):
                    kwargs[name] = resolver_obj.decode(kwargs[name])
            func(self, *args, **kwargs)
        return wrapper

    return decorator

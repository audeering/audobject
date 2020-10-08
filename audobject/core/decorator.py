import functools
import inspect
import typing

from audobject.core import define
from audobject.core.resolver import ValueResolver


def init_decorator(
        sanity_check: bool = True,
        resolvers: typing.Dict[str, typing.Type[ValueResolver]] = None,
):
    r"""Decorator for ``__init__`` function of :class:`audobject.Object`.

    If ``sanity_check==True``, an error will be raised if a parameter
    is not assigned to a class variable of the same name.

    If a dictionary with variable names as keys and
    :class:`audobject.ValueResolver` as values is passed,
    the according variables will be encoded / decoded
    using the according :class:`audobject.ValueResolver`.

    Args:
        sanity_check: perform sanity check
        resolvers: dictionary with resolvers

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
            func(self, *args, **kwargs)
            if sanity_check:
                signature = inspect.signature(func)
                params = [
                    p.name for p in signature.parameters.values()
                    if p.name not in ['self', 'kwargs']
                ]
                params.extend(list(kwargs))
                missing_vars = []
                for var in set(params):
                    if var not in self.__dict__:
                        missing_vars.append(var)
                if len(missing_vars) > 0:
                    raise RuntimeError(
                        f'Found parameter(s)'
                        f' {missing_vars} '
                        f'not assigned to class variable '
                        f'of same name.'
                    )

        return wrapper

    return decorator

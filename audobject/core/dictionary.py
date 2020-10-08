import typing

from audobject.core.object import Object


class Dictionary(Object):
    r"""Dictionary that can be serialized to YAML.

    Args:
        **kwargs: items

    Example:
        >>> # create dictionary
        >>> d = Dictionary(foo='foo', bar='bar')
        >>> # set item
        >>> d['foo'] = 'FOO'
        >>> # get item
        >>> d['foo']
        'FOO'
        >>> # add item
        >>> d['new'] = 1.234
        >>> print(d)
        $audobject.core.dictionary.Dictionary:
          foo: FOO
          bar: bar
          new: 1.234
        >>> d2 = Dictionary(foo='Foo', none=None)
        >>> d.update(d2)
        >>> print(d)
        $audobject.core.dictionary.Dictionary:
          foo: Foo
          bar: bar
          new: 1.234
          none: null

    """  # noqa: E501
    def __init__(
            self,
            **kwargs,
    ):
        for key, value in kwargs.items():
            self[key] = value

    def keys(self) -> typing.KeysView[str]:
        r"""Return the keys."""
        return self.__dict__.keys()

    def items(self) -> typing.ItemsView[str, typing.Any]:
        r"""Return items view."""
        return self.__dict__.items()

    def update(
            self,
            other: 'Dictionary',
    ):
        r"""Update the dictionary with the key/value pairs from other.

        Args:
            other: the other dictionary

        """
        for key, value in other.items():
            self[key] = value

    def values(self) -> typing.ValuesView[typing.Any]:
        r"""Return values."""
        return self.__dict__.values()

    def __contains__(self, key):
        return key in self.__dict__

    def __getitem__(self, name: str) -> typing.Any:
        return self.__dict__[name]

    def __len__(self):
        return len(self.__dict__)

    def __setitem__(self, key: str, value: typing.Any):
        self.__dict__[key] = value

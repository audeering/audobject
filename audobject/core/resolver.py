import datetime
import os
import typing

import audeer
import audobject.core.define as define


DefaultValueType = typing.Union[
    None, str, int, float, bool, list, dict, datetime.datetime,
]


class ValueResolver:
    r"""Abstract resolver class.

    Implement for arguments that are not one of
    ``(None, Object, str, int, float, bool, list, dict)``.

    """
    def __init__(self):
        self.__dict__[define.ROOT_ATTRIBUTE] = None

    @property
    def root(self) -> typing.Optional[str]:
        r"""Root folder.

        Returns root folder when object is serialized to or from a file,
        otherwise ``None`` is returned.

        Returns:
            root directory

        """
        return self.__dict__[define.ROOT_ATTRIBUTE]

    def decode(self, value: DefaultValueType) -> typing.Any:
        r"""Decode value.

        Takes the encoded value and converts it back to its original type.

        Args:
            value: value to decode

        Returns:
            decoded value

        """
        raise NotImplementedError  # pragma: no cover

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

    def encode_type(self) -> type:
        r"""Return encoded type.

        Returns:
            encoded type

        """
        raise NotImplementedError  # pragma: no cover


class FilePathResolver(ValueResolver):
    r"""File path resolver.

    Turns file path to a relative path
    when object is serialized to a file
    and expands it again during reading.

    """

    def decode(self, value: str) -> str:
        r"""Decode file path.

        If object is read from a file,
        this will convert a relative file path
        to an absolute path by expanding it
        with the source directory.

        Args:
            value: relative file path

        Returns:
            expanded file path

        """
        if self.root is not None:
            root = self.root
            value = os.path.join(root, value)
            value = audeer.safe_path(value)
        return value

    def encode(self, value: str) -> str:
        r"""Encode file path.

        If object is written to a file,
        this will convert a file path
        to a path that is relative to the
        target directory.

        Args:
            value: original file path

        Returns:
            relative file path

        """
        if self.root is not None:
            root = self.root
            value = os.path.relpath(value, root)
        return value

    def encode_type(self) -> type:
        r"""Return encoded type.

        Returns:
            encoded type

        """
        return str


class TupleResolver(ValueResolver):
    r"""Tuple resolver."""

    def decode(self, value: list) -> tuple:
        r"""Decodes ``list`` as ``tuple``.

        Args:
            value: list

        Returns:
            tuple

        """
        return tuple(value)

    def encode(self, value: tuple) -> list:
        r"""Encodes ``tuple`` as ``list``.

        Args:
            value: tuple

        Returns:
            list

        """
        return list(value)

    def encode_type(self) -> type:
        r"""Return encoded type.

        Returns:
            encoded type

        """
        return list


class TypeResolver(ValueResolver):
    r"""Type resolver."""

    def decode(self, value: str) -> type:
        r"""Decodes ``str`` as ``type``.

        Args:
            value: type string

        Returns:
            type

        """
        return eval(value)

    def encode(self, value: type) -> str:
        r"""Encodes ``type`` as ``str``.

        Args:
            value: type class

        Returns:
            string

        """
        return str(value)[len("<class '"):-len("'>")]

    def encode_type(self) -> type:
        r"""Return encoded type.

        Returns:
            encoded type

        """
        return str

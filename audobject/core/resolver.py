import datetime
import typing


DefaultValueType = typing.Union[
    None, str, int, float, bool, list, dict, datetime.datetime,
]


class ValueResolver:
    r"""Abstract resolver class.

    Implement for arguments that are not one of
    ``(None, Object, str, int, float, bool, list, dict)``.

    """
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

    def encode_type(self):
        r"""Return encoded type.

        Returns: encoded type

        """
        raise NotImplementedError  # pragma: no cover


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

    def encode_type(self):
        r"""Return encoded type.

        Returns: list

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
        return str

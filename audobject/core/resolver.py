import ast
import datetime
import inspect
import os
import types
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


class FunctionResolver(ValueResolver):
    r"""Function resolver.

    Encodes source code of function and
    dynamically evaluates it when the value is decoded again.

    """

    def decode(self, value: str) -> typing.Callable:
        r"""Decode (lambda) function.

        Args:
            value: source code

        Returns:
            function object

        """
        code = compile(value, '<string>', 'exec')
        for var in code.co_consts:
            if isinstance(var, types.CodeType):
                return types.FunctionType(var, globals())

    def encode(self, value: typing.Callable) -> str:
        r"""Encode (lambda) function.

        Args:
            value: function object

        Returns:
            source code

        """
        if value.__name__ == "<lambda>":
            source = self._get_short_lambda_source(value)
        else:
            source = inspect.getsource(value)
        return source

    def encode_type(self) -> type:
        r"""Returns encoded type.

        Returns:
            encoded type

        """
        return str

    @staticmethod
    def _get_short_lambda_source(lambda_func: typing.Callable):
        """Return the source of a (short) lambda function.
        If it's impossible to obtain, returns None.

        https://gist.github.com/Xion/617c1496ff45f3673a5692c3b0e3f75a

        """
        try:
            source_lines, _ = inspect.getsourcelines(lambda_func)
        except (IOError, TypeError):
            return None

        # skip `def`-ed functions and long lambdas
        if len(source_lines) != 1:
            return None

        source_text = os.linesep.join(source_lines).strip()

        # find the AST node of a lambda definition
        # so we can locate it in the source code
        source_ast = ast.parse(source_text)
        lambda_node = next((node for node in ast.walk(source_ast)
                            if isinstance(node, ast.Lambda)), None)
        if lambda_node is None:  # could be a single line `def fn(x): ...`
            return None

        # HACK: Since we can (and most likely will) get source lines
        # where lambdas are just a part of bigger expressions, they will have
        # some trailing junk after their definition.
        #
        # Unfortunately, AST nodes only keep their _starting_ offsets
        # from the original source, so we have to determine the end ourselves.
        # We do that by gradually shaving extra junk from after the definition.
        lambda_text = source_text[lambda_node.col_offset:]
        lambda_body_text = source_text[lambda_node.body.col_offset:]
        min_length = len('lambda:_')  # shortest possible lambda expression
        while len(lambda_text) > min_length:
            try:
                # What's annoying is that sometimes the junk even parses,
                # but results in a *different* lambda. You'd probably have to
                # be deliberately malicious to exploit it but here's one way:
                #
                #     bloop = lambda x: False, lambda x: True
                #     get_short_lamnda_source(bloop[0])
                #
                # Ideally, we'd just keep shaving until we get the same code,
                # but that most likely won't happen because we can't replicate
                # the exact closure environment.
                code = compile(lambda_body_text, '<unused filename>', 'eval')

                # Thus the next best thing is to assume some divergence due
                # to e.g. LOAD_GLOBAL in original code being LOAD_FAST in
                # the one compiled above, or vice versa.
                # But the resulting code should at least be the same *length*
                # if otherwise the same operations are performed in it.
                if len(code.co_code) == len(lambda_func.__code__.co_code):
                    return lambda_text
            except SyntaxError:
                pass
            lambda_text = lambda_text[:-1]
            lambda_body_text = lambda_body_text[:-1]

        return None


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

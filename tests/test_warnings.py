import pytest

import audobject


audobject.config.SIGNATURE_MISMATCH_WARN_LEVEL = \
    audobject.define.SignatureMismatchWarnLevel.VERBOSE


class MyObject(audobject.Object):
    def __init__(
            self,
            p: str,
            *,
            kw: int = 0,
    ):
        self.p = p
        self.kw = kw


# no version

with pytest.warns(RuntimeWarning):
    o_yaml = MyObject('test').to_yaml_s()


# an optional argument is added

class MyObject(audobject.Object):
    def __init__(
            self,
            p: str,
            new: float = 0.0,
            *,
            kw: int = 0,
    ):
        self.p = p
        self.kw = kw
        self.new = new


with pytest.warns(RuntimeWarning):
    audobject.Object.from_yaml_s(o_yaml)


# an argument is removed

class MyObject(audobject.Object):
    def __init__(
            self,
            *,
            kw: int = 0,
    ):
        self.kw = kw


with pytest.warns(RuntimeWarning):
    audobject.Object.from_yaml_s(o_yaml)


# a mandatory argument is added

class MyObject(audobject.Object):
    def __init__(
            self,
            p: str,
            new: float,
            *,
            kw: int = 0,
    ):
        self.p = p
        self.kw = kw
        self.new = new


with pytest.raises(RuntimeError):
    audobject.Object.from_yaml_s(o_yaml)


audobject.config.SIGNATURE_MISMATCH_WARN_LEVEL = \
    audobject.define.SignatureMismatchWarnLevel.STANDARD

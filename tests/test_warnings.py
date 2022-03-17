import pytest
import warnings

import audeer
import audobject


# Signature mismatch

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
    audobject.from_yaml_s(o_yaml)


audobject.config.SIGNATURE_MISMATCH_WARN_LEVEL = \
    audobject.define.SignatureMismatchWarnLevel.STANDARD


# Package mismatch

warnings.simplefilter('error')

smaller_version = '0.0.0'
installed_version = audobject.__version__
greater_version = '999.9.9'

for level in [
    audobject.define.PackageMismatchWarnLevel.SILENT,
    audobject.define.PackageMismatchWarnLevel.VERBOSE,
    audobject.define.PackageMismatchWarnLevel.STANDARD,
]:
    # no version given -> never warn
    yaml_s = '''
    $audobject.core.testing.TestObject:
      name: test
    '''

    audobject.config.PACKAGE_MISMATCH_WARN_LEVEL = level

    with warnings.catch_warnings():
        audobject.from_yaml_s(yaml_s)

for level, version, expected in [
    # silent -> never warn
    (
        audobject.define.PackageMismatchWarnLevel.SILENT,
        smaller_version,
        False,
    ),
    (
        audobject.define.PackageMismatchWarnLevel.SILENT,
        installed_version,
        False,
    ),
    (
        audobject.define.PackageMismatchWarnLevel.SILENT,
        greater_version,
        False,
    ),
    # standard -> warn if installed version is smaller
    (
        audobject.define.PackageMismatchWarnLevel.STANDARD,
        smaller_version,
        False,
    ),
    (
        audobject.define.PackageMismatchWarnLevel.STANDARD,
        installed_version,
        False,
    ),
    (
        audobject.define.PackageMismatchWarnLevel.STANDARD,
        greater_version,
        True,
    ),
    # verbose -> warn unless versions match
    (
        audobject.define.PackageMismatchWarnLevel.VERBOSE,
        smaller_version,
        True,
    ),
    (
        audobject.define.PackageMismatchWarnLevel.VERBOSE,
        installed_version,
        False,
    ),
    (
        audobject.define.PackageMismatchWarnLevel.VERBOSE,
        greater_version,
        True,
    ),
]:

    yaml_s = f'''
    $audobject.core.testing.TestObject=={version}:
      name: test
    '''

    audobject.config.PACKAGE_MISMATCH_WARN_LEVEL = level

    if expected:
        with pytest.warns(RuntimeWarning):
            audobject.from_yaml_s(yaml_s)
    else:
        with warnings.catch_warnings():
            audobject.from_yaml_s(yaml_s)

audobject.config.PACKAGE_MISMATCH_WARN_LEVEL = \
    audobject.define.PackageMismatchWarnLevel.STANDARD

warnings.simplefilter('default')

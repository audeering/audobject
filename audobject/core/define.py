import datetime


OBJECT_TAG = '$'
VERSION_TAG = '=='
DEFAULT_VALUE_TYPES = (str, int, float, bool, datetime.datetime)
CUSTOM_VALUE_RESOLVERS = '_object_resolvers_'
BORROWED_ATTRIBUTES = '_object_borrowed_'
HIDDEN_ATTRIBUTES = '_object_hidden_'
ROOT_ATTRIBUTE = '_object_root_'


class SignatureMismatchWarnLevel:
    r"""Controls verbosity for signature mismatch.

    A signature mismatch might occur
    if an object is loaded from a different package version
    it was generated with.

    Set via :class:`audobject.config`.

    """
    SILENT = 0
    r"""no warnings"""
    STANDARD = 1
    r"""warn when arguments are removed"""
    VERBOSE = 2
    r"""show all warnings"""

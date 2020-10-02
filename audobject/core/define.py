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

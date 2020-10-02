import audobject.core.define as define


class config:

    SIGNATURE_MISMATCH_WARN_LEVEL = define.SignatureMismatchWarnLevel.STANDARD
    """Controls when a warning is shown in case of a signature mismatch,
    see :class:`audobject.define.SignatureMismatchWarnLevel`."""

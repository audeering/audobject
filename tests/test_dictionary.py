import audobject


def test_dictionary():

    kwargs = {
        'foo': 'foo',
        'bar': 'bar',
    }
    d = audobject.Dictionary(**kwargs)

    assert audobject.core.define.KEYWORD_ARGUMENTS in d.__dict__
    assert audobject.core.define.KEYWORD_ARGUMENTS not in d.arguments

    assert kwargs == dict(d.items())
    assert list(kwargs.keys()) == list(d.keys())
    assert list(kwargs.values()) == list(d.values())

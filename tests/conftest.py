import pytest

import audobject


pytest.COLUMNS = [
    'property1',
    'property2',
    'property3',
]
pytest.PARAMS = [
    {
        pytest.COLUMNS[0]: 'foo',
        pytest.COLUMNS[1]: 'bar',
        pytest.COLUMNS[2]: idx,
    } for idx in range(3)
]
pytest.PARAMETERS = audobject.Parameters().add(
    audobject.Parameter(
        name='foo',
        dtype=str,
        description='a string',
        choices=[None, 'foo'],
    )
).add(
    audobject.Parameter(
        name='bar',
        dtype=int,
        description='an integer',
        default=1,
        version='>=2.0.0',
    )
).add(
    audobject.Parameter(
        name='toggle',
        dtype=bool,
        description='a boolean',
        default=False,
    )
)

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
        value_type=str,
        description='a string',
        choices=[None, 'foo'],
    )
).add(
    audobject.Parameter(
        name='bar',
        value_type=int,
        description='an integer',
        default_value=1,
        version='>=2.0.0',
    )
).add(
    audobject.Parameter(
        name='toggle',
        value_type=bool,
        description='a boolean',
        default_value=False,
    )
)

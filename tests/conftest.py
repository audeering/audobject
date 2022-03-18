import pkg_resources
import pytest
import subprocess
import sys

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
pytest.PARAMETERS = audobject.Parameters(
    foo=audobject.Parameter(
        value_type=str,
        description='a string',
        choices=[None, 'foo'],
    ),
    bar=audobject.Parameter(
        value_type=int,
        description='an integer',
        default_value=1,
        version='>=2.0.0',
    ),
    toggle=audobject.Parameter(
        value_type=bool,
        description='a boolean',
        default_value=False,
    ),
)


def uninstall(
    package: str,
    module: str,
):
    # uninstall package
    subprocess.check_call(
        [
            sys.executable,
            '-m',
            'pip',
            'uninstall',
            '--yes',
            package,
        ]
    )
    # remove module
    for m in list(sys.modules):
        if m.startswith(module):
            sys.modules.pop(m)
    # force pkg_resources to re-scan site packages
    pkg_resources._initialize_master_working_set()


@pytest.fixture(scope='session', autouse=True)
def cleanup():
    yield
    # uninstall package temporarily installed by test_install.py
    uninstall('audbackend', 'audbackend')
    uninstall('dohq-artifactory', 'artifactory')

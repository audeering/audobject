import subprocess
import sys

import pytest

import audobject


PACKAGE = 'audbackend'

yaml_with_version = f'''
${PACKAGE}.core.filesystem.FileSystem==0.3.12:
  host: ~/host
  repository: repo
'''

yaml_without_version = f'''
{PACKAGE}.core.filesystem.FileSystem:
  host: ~/host
  repository: repo
'''


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    # uninstall audbackend
    subprocess.check_call(
        [
            sys.executable,
            '-m',
            'pip',
            'uninstall',
            '--yes',
            PACKAGE,
        ]
    )
    # remove from module cache
    remove = []
    for module in sys.modules:
        if module.startswith(PACKAGE):
            remove.append(module)
    for module in remove:
        sys.modules.pop(module)


@pytest.mark.parametrize(
    'yaml_s',
    [
        yaml_with_version,
        yaml_without_version,
    ],
)
def test(yaml_s):
    with pytest.raises(ModuleNotFoundError):
        audobject.from_yaml_s(
            yaml_s,
            auto_install=False,
        )
    audobject.from_yaml_s(
        yaml_s,
        auto_install=True,
    )

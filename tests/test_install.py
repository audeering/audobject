import pkg_resources
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
    for module in list(sys.modules):
        if module.startswith(PACKAGE):
            sys.modules.pop(module)
    # force pkg_resources to re-scan site packages
    pkg_resources._initialize_master_working_set()


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
    # install missing packages
    audobject.from_yaml_s(
        yaml_s,
        auto_install=True,
    )
    # also works if all packages are installed
    audobject.from_yaml_s(
        yaml_s,
        auto_install=True,
    )

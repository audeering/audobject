import subprocess
import sys

import pytest

import audobject


yaml_with_version = '''
$opensmile.core.smile.Smile==2.4.1:
  feature_set: ComParE_2016
  feature_level: Functionals
  options: {}
  sampling_rate: null
  channels:
  - 0
  mixdown: false
  resample: false
'''


yaml_without_version = '''
$opensmile.core.smile.Smile:
  feature_set: ComParE_2016
  feature_level: Functionals
  options: {}
  sampling_rate: null
  channels:
  - 0
  mixdown: false
  resample: false
'''


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    # uninstall opensmile package...
    subprocess.check_call(
        [
            sys.executable,
            '-m',
            'pip',
            'uninstall',
            '--yes',
            'opensmile',
        ]
    )
    # ...and remove from module cache
    remove = []
    for module in sys.modules:
        if module.startswith('opensmile'):
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

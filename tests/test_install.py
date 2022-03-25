import os

import pytest

import audobject

from conftest import uninstall


@pytest.mark.parametrize(
    'yaml_s, package, module',
    [
        (  # package and module do not match
            '''
            $dohq-artifactory:artifactory.ArtifactoryPath:
              token: token
            ''',
            'dohq-artifactory',
            'artifactory',
        ),
        (  # package and module match
            '''
            $audbackend.core.filesystem.FileSystem:
              host: ~/host
              repository: repo
            ''',
            'audbackend',
            'audbackend',
        ),
        (  # with package version and as nested object
            '''$audobject.core.testing.TestObject:
              name: test
              backend:
                $audbackend.core.filesystem.FileSystem==0.3.12:
                  host: ~/host
                  repository: repo
            ''',
            'audbackend',
            'audbackend',
        )
    ],
)
def test(tmpdir, yaml_s, package, module):

    # fails because of missing packages
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
    # still works when packages are installed
    audobject.from_yaml_s(
        yaml_s,
        auto_install=True,
    )
    # uninstall package
    uninstall(package, module)

    # repeat, but this time test from file
    path = os.path.join(tmpdir, 'tmp.yaml')
    with open(path, 'w') as fp:
        fp.write(yaml_s)

    # fails because of missing packages
    with pytest.raises(ModuleNotFoundError):
        audobject.from_yaml(
            path,
            auto_install=False,
        )
    # install missing packages
    audobject.from_yaml(
        path,
        auto_install=True,
    )
    # still works when packages are installed
    audobject.from_yaml(
        path,
        auto_install=True,
    )
    # uninstall package
    uninstall(package, module)

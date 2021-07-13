import os
import shutil

import audeer
import audobject


class ObjectWithFile(audobject.Object):

    @audobject.init_decorator(
        resolvers={
            'path': audobject.FilePathResolver,
        }
    )
    def __init__(
            self,
            path: str,
    ):
        self.path = path


def test_filepath(tmpdir):

    root = os.path.join(tmpdir, 'test')
    new_root = os.path.join(tmpdir, 'some', 'where', 'else')

    # create resource file
    resource_path = os.path.join(root, 're', 'source.txt')
    audeer.mkdir(os.path.dirname(resource_path))
    with open(resource_path, 'w'):
        pass

    # create object and serialize
    yaml_path = os.path.join(root, 'yaml', 'object.yaml')
    o = ObjectWithFile(resource_path)
    o.to_yaml(yaml_path, include_version=False)

    # move files to another location
    shutil.move(root, new_root)
    new_yaml_path = os.path.join(new_root, 'yaml', 'object.yaml')

    # re-instantiate object from new location and assert path exists
    o2 = audobject.Object.from_yaml(new_yaml_path)
    assert isinstance(o2, ObjectWithFile)
    assert os.path.exists(o2.path)

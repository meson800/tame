import os
import sys
import pytest

import tame.core

from test_helpers import touch

def test_metadata_arg_failure():
    """
    Ensures that if we pass neither a filename or a
    metadata object, we raise the proper exception
    """
    with pytest.raises(ValueError):
        meta = tame.core.Metadata()

def test_barebones_file(tmpdir):
    """
    Ensures that we can load a metadata
    file with the minimum required metadata
    entries, a type.
    """
    tmpdir = tmpdir.strpath

    touch(os.path.join(tmpdir, 'root.yaml'))
    with open(os.path.join(tmpdir, 'simple.yaml'), 'w') as f:
        f.write('type: test')
    meta = tame.core.Metadata(filename=os.path.join(tmpdir, 'simple.yaml'))
    assert meta.type == 'test'

def test_barebones_yaml_source():
    """
    Same test as 'test_barebones_file', except checking
    that we recognize directly written yaml source
    """
    yaml = 'type: test'
    meta = tame.core.Metadata(yaml_source=yaml)
    assert meta.type == 'test'

def test_type_required():
    """
    Ensures that a YAML file without a type key fails
    validation.
    """
    yaml = 'name: foo\nuid: bar\n'
    with pytest.raises(tame.core.InconsistentMetadataError):
        meta = tame.core.Metadata(yaml_source=yaml)

def test_special_keyvalues():
    """
    Ensures that all special keyvalue pairs are recognized.
    These are type, files, name, uid, parent.
    """
    yaml = """
    type: test
    name: foo
    uid: bar
    files:
      - test_file.yaml
    parent: 
      - foobar
    """
    meta = tame.core.Metadata(yaml_source=yaml)
    assert meta.type == 'test'
    assert meta.name == 'foo'
    assert meta.uid == 'bar'
    assert meta.files == ['test_file.yaml']
    assert meta.parent == ['foobar']

def test_name_required_as_string():
    """
    Ensures that the 'name' key is passed as a string.
    """
    yaml = """
    type: test
    name:
      - foo
      - bar
    """
    with pytest.raises(tame.core.InconsistentMetadataError):
        meta = tame.core.Metadata(yaml_source=yaml)

def test_uid_required_as_string():
    """
    Ensures that the 'uid' key is passed as a string.
    """
    yaml = """
    type: test
    uid:
      - foo
      - bar
    """
    with pytest.raises(tame.core.InconsistentMetadataError):
        meta = tame.core.Metadata(yaml_source=yaml)

def test_files_required_as_list():
    """
    Ensures that the 'files' key must be passed as a list
    """
    yaml = """
    type: test
    files: foobar
    """
    with pytest.raises(tame.core.InconsistentMetadataError):
        meta = tame.core.Metadata(yaml_source=yaml)

def test_parent_required_as_list():
    """
    Ensures that the 'parent' key is passed as a list
    """
    yaml = """
    type: test
    parent: foobar
    """
    with pytest.raises(tame.core.InconsistentMetadataError):
        meta = tame.core.Metadata(yaml_source=yaml)

def test_user_key_loading():
    """
    Ensure that user keyvalue pairs are loaded properly.
    """
    yaml = """
    type: test
    user: userval
    """
    meta = tame.core.Metadata(yaml_source=yaml)
    assert 'user' in meta.data
    assert meta.data['user'] == 'userval'



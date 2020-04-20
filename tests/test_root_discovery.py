import os
import sys
import pytest

import tame.core

def touch(filename):
    """Creates the desired file by writing a newline"""
    with open(filename, 'w') as f:
        f.write('\n')

def test_simple_find_root(tmpdir):
    """Tests if a simple flat hierarchy tame.yaml file is found"""
    touch(os.path.join(tmpdir.strpath, 'tame.yaml'))
    # Does not throw exception on success
    print(tame.core.find_root_yaml(tmpdir.strpath))

def test_root_not_found(tmpdir):
    """
    Makes sure that a UntrackedRepositoryError is raised
    when tame.yaml does not exist
    """
    with pytest.raises(tame.core.UntrackedRepositoryError):
        print(tame.core.find_root_yaml(tmpdir.strpath))

def test_find_root_recursive(tmpdir):
    """
    Makes sure that the root file can be found by searching upward
    """
    os.makedirs(os.path.join(tmpdir.strpath, 'nested', 'deeply'))
    touch(os.path.join(tmpdir.strpath, 'tame.yaml'))
    touch(os.path.join(tmpdir.strpath, 'nested', 'metadata.yaml'))
    touch(os.path.join(tmpdir.strpath, 'nested', 'deeply', 'test.yaml'))
    touch(os.path.join(tmpdir.strpath, 'nested', 'deeply', 'test.jpg'))
    print(tame.core.find_root_yaml(os.path.join(tmpdir.strpath, 'nested')))
    print(tame.core.find_root_yaml(os.path.join(tmpdir.strpath, 'nested', 'deeply')))
    print(tame.core.find_root_yaml(os.path.join(tmpdir.strpath, 'nested', 'metadata.yaml')))

def test_permission_denied(tmpdir):
    """
    Makes sure that we correctly stop searching upward if we reach a
    directory without read permission
    """
    if sys.platform.startswith("win"):
        pytest.skip('Unable to modify file permissions on Windows')
    os.makedirs(os.path.join(tmpdir.strpath, 'nested', 'again'))
    touch(os.path.join(tmpdir.strpath, 'tame.yaml'))
    touch(os.path.join(tmpdir.strpath, 'nested', 'again', 'test.yaml'))
    os.chmod(os.path.join(tmpdir.strpath, 'tame.yaml'), 0o000)
    os.chmod(tmpdir.strpath, 0o000)
    with pytest.raises(tame.core.UntrackedRepositoryError):
        print(tame.core.find_root_yaml(os.path.join(tmpdir.strpath, 'nested', 'again', 'test.yaml')))


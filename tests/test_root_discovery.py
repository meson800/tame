import os
import pytest

import tame.core

def touch(filename):
    """Creates the desired file by writing a newline"""
    with open(filename, 'w') as f:
        f.write('\n')

def test_simple_find_root(tmpdir):
    """Tests if a simple flat hierarchy tame.yaml file is found"""
    touch(os.path.join(tmpdir, 'tame.yaml'))
    # Does not throw exception on success
    print(tame.core.find_root_yaml(tmpdir))

def test_root_not_found(tmpdir):
    """
    Makes sure that a UntrackedRepositoryError is raised
    when tame.yaml does not exist
    """
    with pytest.raises(tame.core.UntrackedRepositoryError):
        print(tame.core.find_root_yaml(tmpdir))

def test_find_root_recursive(tmpdir):
    """
    Makes sure that the root file can be found by searching upward
    """
    os.makedirs(os.path.join(tmpdir, 'nested', 'deeply'))
    touch(os.path.join(tmpdir, 'tame.yaml'))
    touch(os.path.join(tmpdir, 'nested', 'metadata.yaml'))
    touch(os.path.join(tmpdir, 'nested', 'deeply', 'test.yaml'))
    touch(os.path.join(tmpdir, 'nested', 'deeply', 'test.jpg'))
    print(tame.core.find_root_yaml(os.path.join(tmpdir, 'nested')))
    print(tame.core.find_root_yaml(os.path.join(tmpdir, 'nested', 'deeply')))
    print(tame.core.find_root_yaml(os.path.join(tmpdir, 'nested', 'metadata.yaml')))

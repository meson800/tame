from pathlib import Path

import tame.core

def touch(filename):
    """Creates the desired file by writing a newline"""
    with open(str(filename), 'w') as f:
        f.write('\n')

def init_cache(tmpdir):
    """
    Given the temporary directory, returns a tuple
    that encodes the MetadataCache object and a Path-ified
    version of tmpdir, after creating the root.yaml file
    """
    tmpdir = Path(tmpdir.strpath)
    touch(tmpdir / 'tame.yaml')
    cache = tame.core.MetadataCache(tmpdir / 'tame.yaml')
    return (tmpdir, cache)

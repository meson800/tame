from pathlib import Path
import pytest

import tame.core

from test_helpers import touch

def init_cache(tmpdir):
    """
    Given the temporary directory, returns a tuple
    that encodes the MetadataCache object and a Path-ified
    version of tmpdir, after creating the root.yaml file
    """
    tmpdir = Path(tmpdir.strpath)
    touch(tmpdir / 'root.yaml')
    cache = tame.core.MetadataCache(tmpdir / 'root.yaml')
    return (tmpdir, cache)

def test_simple_cache_loading(tmpdir):
    """
    Ensures that we can do simple single-file addition
    into the cache
    """
    tmpdir, cache = init_cache(tmpdir)

    with open(tmpdir / 'test.yaml', 'w') as f:
        f.write("""
        type: foo
        name: bar
        user_key: user_val
        """)
    cache.add_metadata(Path('test.yaml'))

def test_uid_collision(tmpdir):
    """
    Ensures that the cache loader throws an error
    if two metadata files are loaded with the same type/uid pair.
    """
    tmpdir, cache = init_cache(tmpdir)

    with open(tmpdir / 'test1.yaml', 'w') as f:
        f.write("""
        type: foo
        uid: bar
        userkey1: userval1
        """)
    with open(tmpdir / 'test2.yaml', 'w') as f:
        f.write("""
        type: foo
        uid: bar
        userkey2: userval2
        """)
    cache.add_metadata(Path('test1.yaml'))
    with pytest.raises(tame.core.InconsistentMetadataError):
        cache.add_metadata(Path('test2.yaml'))

def test_non_uid_collisions(tmpdir):
    """
    Ensures that two files without a UID set do not conflict, as do
    two metadata files that have the same UID but different type.
    """
    tmpdir, cache = init_cache(tmpdir)

    with open(tmpdir / 'test1.yaml', 'w') as f:
        f.write("""
        type: foo
        uid: test
        """)
    with open(tmpdir / 'test2.yaml', 'w') as f:
        f.write("""
        type: bar
        uid: test
        """)
    with open(tmpdir / 'test3.yaml', 'w') as f:
        f.write("""
        type: baz
        userkey1: userval1
        """)
    with open(tmpdir / 'test4.yaml', 'w') as f:
        f.write("""
        type: baz
        userkey1: userval1
        """)
    cache.add_metadata(Path('test1.yaml'))
    cache.add_metadata(Path('test2.yaml'))
    cache.add_metadata(Path('test3.yaml'))
    cache.add_metadata(Path('test4.yaml'))

def test_name_noncollision(tmpdir):
    """
    Ensures that two files do not collide if they have the same name/type
    pair, as long as they either have blank UIDs or different UIDs
    """
    tmpdir, cache = init_cache(tmpdir)

    with open(tmpdir / 'test1.yaml', 'w') as f:
        f.write("""
        type: foo
        name: bar
        """)
    with open(tmpdir / 'test2.yaml', 'w') as f:
        f.write("""
        type: foo
        name: bar
        """)
    with open(tmpdir / 'test3.yaml', 'w') as f:
        f.write("""
        type: foo
        name: bar
        uid: baz
        """)
    cache.add_metadata(Path('test1.yaml'))
    cache.add_metadata(Path('test2.yaml'))
    cache.add_metadata(Path('test3.yaml'))


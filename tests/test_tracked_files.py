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
    touch(tmpdir / 'tame.yaml')
    cache = tame.core.MetadataCache(tmpdir / 'tame.yaml')
    return (tmpdir, cache)

def test_skip_fileloading(tmpdir):
    """
    Checks that an invalid tracked file does not raise
    an error when we are not checking tracked files.
    """
    t = Path(tmpdir.strpath)
    with open(str(t / 'meta1.yaml'), 'w') as f:
        f.write("""
        type: plasmid
        name: p001
        files:
          - invalid.gb
        """)
    tmpdir, cache = init_cache(tmpdir)
    cache.validate_chain(should_verify_files=False)

def test_invalid_file_error(tmpdir):
    """
    Checks that an invalid tracked file raises a
    InconsistentMetadataError when a tracked file
    does not exist.
    """
    t = Path(tmpdir.strpath)
    (t / 'inner').mkdir()
    with open(str(t / 'meta1.yaml'), 'w') as f:
        f.write("""
        type: plasmid
        name: p001
        files:
          - invalid.gb
        """)
    with open(str(t / 'meta2.yaml'), 'w') as f:
        f.write("""
        type: plasmid
        name: p002
        files:
          - inner/valid.gb
        """)
    with open(str(t / 'inner' / 'valid.gb'), 'w') as f:
        f.write('Hi!')
    
    tmpdir, cache = init_cache(tmpdir)
    cache.validate_chain('meta2.yaml')
    with pytest.raises(tame.core.InconsistentMetadataError):
        cache.validate_chain('meta1.yaml')

def test_file_glob(tmpdir):
    """
    Checks that file globs can be specified in the files key.
    """
    t = Path(tmpdir.strpath)
    (t / 'invalid').mkdir()
    (t / 'valid').mkdir()
    with open(str(t / 'meta1.yaml'), 'w') as f:
        f.write("""
        type: plasmid
        name: p001
        files:
          - invalid/*.gb
        """)
    with open(str(t / 'meta2.yaml'), 'w') as f:
        f.write("""
        type: plasmid
        name: p002
        files:
          - valid/*.gb
        """)
    with open(str(t / 'valid' / 'first.gb'), 'w') as f:
        f.write('Hi!')
    with open(str(t / 'valid' / 'second.gb'), 'w') as f:
        f.write('Hi there!')

    tmpdir, cache = init_cache(tmpdir)
    with pytest.raises(tame.core.InconsistentMetadataError):
        cache.validate_chain('meta1.yaml')
    cache.validate_chain('meta2.yaml')

def test_multi_file(tmpdir):
    """
    Checks that multiple tracked files are correctly tracked.
    """
    t = Path(tmpdir.strpath)
    (t / 'inner').mkdir()
    with open(str(t / 'meta1.yaml'), 'w') as f:
        f.write("""
        type: plasmid
        name: p001
        files:
          - simple.gb
          - inner/*.gb
        """)
    with open(str(t / 'simple.gb'), 'w') as f:
        f.write('Hi!')

    tmpdir, cache = init_cache(tmpdir)
    with pytest.raises(tame.core.InconsistentMetadataError):
        cache.validate_chain()

    with open(str(t / 'inner' / 'inner.gb'), 'w') as f:
        f.write('Hi!')
    cache.validate_chain()


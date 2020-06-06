from pathlib import Path
import pytest

import _tame_walk

from test_helpers import touch

def shared_init(tmpdir):
    """
    Given a temporary directory, returns the Path-ified
    version of the tmpdir, after filling it with a file
    system designed to test the _tame_walk C extension.

    Also returns paths that should be valid under inclusion
    of both .yaml and .meta
    """
    tmpdir = Path(tmpdir.strpath)
    (tmpdir / 'nested1' / 'nested2').mkdir(parents=True)
    valid = [tmpdir / 'tame.yaml',
             tmpdir / 'nested1' / 'another.yaml',
             tmpdir / 'nested1' / 'nested2' / 'valid.yaml']
    expanded_valid = valid + [
             tmpdir / 'nested1' / 'alternate.meta',
             tmpdir / 'nested1' / 'nested2' / 'separate.meta']

    touch(tmpdir / 'notayaml.lmay')
    touch(tmpdir / 'nested1' / 'nested2' / 'invalid.blah')

    for path in expanded_valid:
        touch(path)

    return tmpdir, valid, expanded_valid

def test_full_sweep(tmpdir):
    """
    Checks that the C extension can return all
    default .yaml files, with both styles of
    passed arguments
    """
    tmpdir, v, _ = shared_init(tmpdir)
    results = set(_tame_walk.walk(str(tmpdir), '.yaml'))
    alt_results = set(_tame_walk.walk(str(tmpdir), ['.yaml']))
    assert results == alt_results

    pathified_results = {Path(s) for s in results}
    for path in v:
        assert(path in pathified_results)

def test_alternate_extensions(tmpdir):
    """
    Validates that multiple different extensions
    can be requested.
    """
    tmpdir, _, ev = shared_init(tmpdir)
    results = set(_tame_walk.walk(str(tmpdir), ['.yaml', '.meta']))

    pathified_results = {Path(s) for s in results}
    for path in ev:
        assert(path in pathified_results)

def test_exceptional_arg_pass(tmpdir):
    """
    Ensures that the C extension returns sane extensions
    when given invalid inputs
    """
    tmpdir, _, _ = shared_init(tmpdir)

    with pytest.raises(TypeError):
        _tame_walk.walk()
    with pytest.raises(TypeError):
        _tame_walk.walk(str(tmpdir))
    with pytest.raises(TypeError):
        _tame_walk.walk(tmpdir, '.yaml')
    with pytest.raises(TypeError):
        _tame_walk.walk(str(tmpdir), 3.14)
    with pytest.raises(TypeError):
        _tame_walk.walk(str(tmpdir), ['.yaml', 3.14])

    with pytest.raises(RuntimeError):
        print(_tame_walk.walk('blahblahiamnotapath', '.yaml'))


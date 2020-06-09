from pathlib import Path
import yaml

import tame.error_format

import pytest

def test_relative_filename_func(tmpdir):
    """
    Ensures that the function that converts filenames
    relative to the current working directory works
    properly.
    """
    tmpdir = Path(tmpdir.strpath)

    assert tame.error_format.simplify_filename() == 'INLINE_YAML'
    assert (tame.error_format.simplify_filename(None) ==
            'INLINE_YAML')
    test_path = Path.cwd() / 'test.yaml'
    assert (str(tame.error_format.simplify_filename(test_path)) ==
            'test.yaml')
    test_path2 = tmpdir / 'test.yaml'
    assert (str(tame.error_format.simplify_filename(test_path2)) ==
            str(test_path2))

def test_scanner_error():
    """
    Ensures that the error formatter can handle
    YAML scanner errors
    """
    yaml_source = """
        type: digest_gel
        name: digest_products
        date: 2020-02-06
        lanes:
          - source: test
            expected: ?
        """
    try:
        test_dict = yaml.safe_load(yaml_source)
    except yaml.scanner.ScannerError as err:
        print(tame.error_format.format_yaml_error(yaml_source, str(err)))


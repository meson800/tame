import yaml

import tame.error_format

import pytest

def test_scanner_error():
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

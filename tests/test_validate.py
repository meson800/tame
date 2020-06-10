from pathlib import Path
import pytest

import tame.validate

def test_validate_yaml_errors(pytestconfig):
    """
    Checks that repos with YAML validation errors
    are handled.
    """
    repo_path = Path(pytestconfig.rootdir.strpath) / 'tests/test_repos/yaml_errors'
    with pytest.raises(tame.core.InconsistentMetadataError):
        tame.validate.validate_path(str(repo_path))

def test_validate_parent_errors(pytestconfig):
    """
    Checks that repos with parent erros fail when
    validated.
    """
    repo_path = Path(pytestconfig.rootdir.strpath) / 'tests/test_repos/parent_errors'
    with pytest.raises(tame.core.InconsistentMetadataError):
        tame.validate.validate_path(str(repo_path))

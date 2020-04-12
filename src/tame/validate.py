"""
Handles validation to ensure that metadata files
are properly formatted, have proper parent relationships,
and track currently included files.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
import os

from . import core


def _init_argparse_(subparser):
    subparser.add_argument('path', help='File or directory to validate.\
            All YAML files found recursively from this directory are validated')
    subparser.add_argument('-m', '--metadata-only', action='store_true', help='\
            does not attempt to validate the presence of linked files')


def _dispatch_validate_(args):
    """Calls our internal API using provided command line args"""
    validate_path(args.path, args.metadata_only)


def validate_path(path, metadata_only=False):
    """
    Validates that the given YAML file or all
    YAML files recursively reachable from a given directory
    have correct YAML syntax, have correct parent relationships,
    and all linked files are in place.

    Args:
        path: path-like object (str, bytes) containing a file or
              directory to validate

        metadata_only: Set to true to skip verifying that linked
                       files are in place

    Returns:
        A list of validation failures or None if no validation failures exist.

    Raises:
        UntrackedRepositoryError: If the given path is not within a tracked repository.
    """
    root = core.find_root_yaml(path)

    # If this is a file, attempt to validate it
    if os.path.isfile(path):
        core.Metadata(filename=path)


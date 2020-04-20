"""
Includes key shared functions used by other internal Tame modules.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
import os
import yaml


class UntrackedRepositoryError(RuntimeError):
    """
    Runtime error thrown when the root tame.yaml file
    was not found.

    Like git, we want to restrict tracked metadata to
    a certain overall directory (repository). We mark
    the top-level directory in the repository with a
    tame.yaml file.
    """

class InconsistentMetadataError(RuntimeError):
    """
    Runtime error thrown when a loaded piece of metadata
    is either not valid YAML or does not follow the TAME
    syntax.
    """

class MissingParentError(RuntimeError):
    """
    Runtime error thrown when metadata attempts to
    reference a missing parent piece of metadata
    """

class Metadata:
    """
    Class that represents a piece of metadata (e.g. a single YAML document).
    The only required key in a piece of metadata is its `type`, a string
    describing what this piece of metadata represents.

    Special tags:
    - type (required): String describing what this piece of metadata represents
    - files (optional): A list of files to be tracked as attached to this metadata.
    - name (optional): A (non-unique) name for this piece of metadata.
    - uid (optional): A name for this metadata that is enforced to be unique.
    - parent (optional): A list of different parent metadata files
    """
    def __init__(self, yaml_source=None, filename=None):
        """
        Given a YAML document, constructs a Metadata object. The loaded
        YAML must not have any errors and must include at least the type key.

        Args:
            yaml_source: A byte string, Unicode string, open binary file, or
                open text file object representing the YAML document. If
                passed a string, this must be the actual file content!
            filename: A path-like object representing the on-disk location
                of the metadata object.

        Returns:
            A properly constructed Metadata object

        Raises:
            RuntimeError: if both yaml_source and filename are not passed.
            InconsistentMetadataError: If the various special tags do not have
                the correct type, or are missing if required.
        """
        if yaml_source is None and filename is None:
            raise RuntimeError('Must specify yaml source or filename to load function!')
        if yaml_source is None:
            with open(filename) as yaml_file:
                yaml_source = yaml_file.read()
        # Read in with pyyaml
        yaml_dict = yaml.safe_load(yaml_source)

        if 'type' not in yaml_dict or not isinstance(yaml_dict['type'], str):
            raise InconsistentMetadataError('Type of metadata must be provided' +
                                            ' as a string')
        # Setup default arguments
        self.type = yaml_dict['type']
        del yaml_dict['type']
        self.name = ''
        self.uid = ''
        self.parent = {}
        self.files = []
        # Replace them as needed
        if 'name' in yaml_dict:
            if not isinstance(yaml_dict['name'], str):
                raise InconsistentMetadataError(
                    'name key is special: value must be provided as a string')
            self.name = yaml_dict['name']
            del yaml_dict['name']
        if 'uid' in yaml_dict:
            if not isinstance(yaml_dict['uid'], str):
                raise InconsistentMetadataError(
                    'uid key is special: value must be provided as a string')
            self.uid = yaml_dict['uid']
            del yaml_dict['uid']
        if 'parent' in yaml_dict:
            if not isinstance(yaml_dict['parent'], list):
                raise InconsistentMetadataError(
                    'parent key is special: value must be provided as a list')
            self.parent = yaml_dict['parent']
            del yaml_dict['parent']
        if 'files' in yaml_dict:
            if not isinstance(yaml_dict['files'], list):
                raise InconsistentMetadataError(
                    'files key is special: value must be provided as a list')
            self.files = yaml_dict['files']
            del yaml_dict['files']
        self.

def find_root_yaml(path=None):
    """
    Starting from a given path or the current working directory,
    walks up the filesystem until a 'root' tame.yaml file is found.
    The path to this root YAML file is returned.

    Args:
        path: path-like object (str, bytes) to start the recursive search.
              Defaults to the current working directory if not set.
    Returns:
        A path-like object to the root file.

    Raises:
        UntrackedRepositoryError: if the search path could not find a root tame.yaml file.
    """
    if path is None:
        path = os.getcwd()
    # Keep path as-is if we were passed a directory
    if os.path.isdir(path):
        current_dir = path
    else:
        current_dir = os.path.dirname(path)

    while not os.path.isfile(os.path.join(current_dir, 'tame.yaml')):
        up_dir = os.path.join(current_dir, os.pardir)
        # Make sure we didn't reach the filesystem root
        if os.path.samefile(os.path.realpath(up_dir),
                            os.path.realpath(current_dir)):
            raise UntrackedRepositoryError("No root 'tame.yaml' file found")
        # otherwise, continue searching
        current_dir = up_dir
    return os.path.join(current_dir, 'tame.yaml')

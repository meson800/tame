"""
Includes key shared functions used by other internal Tame modules.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
import os


class UntrackedRepositoryError(RuntimeError):
    """
    Runtime error thrown when the root tame.yaml file
    was not found.

    Like git, we want to restrict tracked metadata to
    a certain overall directory (repository). We mark
    the top-level directory in the repository with a
    tame.yaml file.
    """


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
    try:
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
    except PermissionError as e:
        print(e)
        raise UntrackedRepositoryError("No root 'tame.yaml' found due to permission denied error")

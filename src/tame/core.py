"""
Includes key shared functions used by other internal Tame modules.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
from pathlib import Path
import yaml

import _tame_walk
from . import error_format



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
    rules.
    """

class MetadataLookupError(RuntimeError):
    """
    Runtime error thrown when a lookup for a piece
    of metadata fails, often through a missing parent
    """

def _import_yaml(yaml_source=None, filename=None):
    """
    Given a YAML document, returns a Python dictionary
    to the imported yaml document.

    Args:
    -----
    yaml_source: A byte string, Unicode string, open binary file, or
        open text file object representing the YAML document.
    filename: A path-like object representing the on-disk location
        of the metadata object.

    Returns:
    --------
    A dictionary containing the parsed document.

    Raises:
    -------
    An InconsistentMetadataError if a problem occured on loading.
    A ValueError if neither yaml_source/filename args are given.
    """
    if yaml_source is None and filename is None:
        raise ValueError('Must specify yaml source or filename to load function!')
    if yaml_source is None:
        with open(str(filename)) as yaml_file:
            yaml_source = yaml_file.read()
    # Read in with pyyaml
    try:
        yaml_dict = yaml.safe_load(yaml_source)
        return yaml_dict
    except (yaml.scanner.ScannerError,
            yaml.parser.ParserError) as err:
        if filename is None:
            out_file = None
        else:
            out_file = str(filename)
        raise InconsistentMetadataError(error_format.format_yaml_error(
            str(err), out_file))

class Metadata: # pylint: disable=too-few-public-methods
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
        yaml_dict = _import_yaml(yaml_source, filename)

        if 'type' not in yaml_dict or not isinstance(yaml_dict['type'], str):
            raise InconsistentMetadataError('Type of metadata must be provided' +
                                            ' as a string')
        # Setup default arguments
        self.type = yaml_dict['type']
        del yaml_dict['type']
        self.name = ''
        self.uid = ''

        if filename is None:
            filename = 'INLINE_YAML'
        self.filename = filename

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
        # Set remaining user metadata
        self.data = yaml_dict

class MetadataTree: # pylint: disable=too-few-public-methods
    """
    Class that stores a mirrored version of the
    metadata directory, loaded on demand. This tree
    stores both metadata objects, if present at a file
    location, along with storing last updated timestamps
    """
    def __init__(self, node_path_element, last_update_timestamp):
        """
        Initalizes the internal details of the tree.

        Args:
        -----
        node_path_element: The part of the filename
            recognized by this part of the tree. Joining
            all of the parts of the path with pathlib would
            give the path relative to the root.
        last_update_timestamp: The timestamp for the last time
            the file or directory was updated.
        """
        self.path_element = node_path_element
        self.children = {}
        self.timestamp = last_update_timestamp
        self.metadata_index = None

class MetadataCache:
    """
    Class that represents a cache of metadata objects. This class
    stores Metadata objects, indexed by filename (from the root), name,
    and by UID.

    Key to using this cache is the 'lookup' function, which either gets a
    loaded metadata object from the cache, or attempts to search the metadata
    repository for the desired object.

    Objects are stored internally through a layer of indirection; each is
    stored indexed in a list. Lookups are facilitated
    primarily by a type dictionary, which contains subdictionaries:
    a name dictionary (storing _lists_ of metadata objects) and a UID
    dictionary (must store single indicies).
    Filesystem paths are handled in a tree structure.
    """
    def __init__(self, root):
        """
        Given a path to the root file, constructs the internal
        structures needed for the cache, and walks down from the root
        directory, storing located metadata files.

        Args:
        -----
        root: A path-like object encoding the filename of the root.yaml file
        """
        self.root_filename = Path(root)
        self.root_dir = Path(root).parent.resolve()
        with open(str(self.root_filename)) as yaml_file:
            self.root_settings = yaml.safe_load(yaml_file.read())

        self._cache = []
        self._filename_tree = MetadataTree(self.root_dir,
                                           self.root_dir.stat().st_mtime)
        self._type_table = {}

        # Initiate a filesystem scan
        files_to_load = _tame_walk.walk(str(self.root_dir), '.yaml')
        files_set = {Path(f) for f in files_to_load}
        # Remove the root yaml file, as it must be there.
        if self.root_dir / 'tame.yaml' not in files_set:
            raise RuntimeError("Loading of root file failed")
        files_set.remove(self.root_dir / 'tame.yaml')

        error_accum = []
        for cur_f in files_set:
            rel_filename = cur_f.relative_to(self.root_dir)
            try:
                self.add_metadata(rel_filename)
            except InconsistentMetadataError as err:
                error_accum.append(str(err))
        if len(error_accum) > 0:
            raise InconsistentMetadataError('\n'.join(error_accum))


    def add_metadata(self, filename):
        """
        Given a filename, reads the metadata at that file
        and adds it to the internal caches.

        If that metadata file has already been loaded, we silently
        skip loading.

        Args:
        -----
        filename: A Path object containing a filename of a metadata
            file to load, specified relative to the directory including
            the root.
        """
        # Add to the filename tree
        tree_entry = self._filename_tree
        cur_path = self.root_dir

        filename = (self.root_dir / filename).resolve()
        for part in filename.relative_to(self.root_dir).parts:
            cur_path = cur_path / Path(part)
            if part not in tree_entry.children:
                tree_entry.children[part] = MetadataTree(cur_path,
                                                         cur_path.stat().st_mtime)
            tree_entry = tree_entry.children[part]

        # Skip if we've already loaded this piece of metdata.
        if tree_entry.metadata_index is not None:
            return

        # Otherwise, attempt to load it
        new_metadata = Metadata(filename=self.root_dir / filename)

        new_index = len(self._cache)
        self._cache.append(new_metadata)

        # Create subdictionaries if necessary
        m_type = new_metadata.type
        m_name = new_metadata.name
        m_uid = new_metadata.uid
        if m_type not in self._type_table:
            self._type_table[m_type] = {
                'name': {},
                'uid': {}}
        # Check that type/UID pair is unique (if we have a UID)
        if m_uid:
            if m_uid in self._type_table[m_type]['uid']:
                raise InconsistentMetadataError(
                    ('Metadata with type={}, UID={}' +
                     ' does not have a unique type/UID pair!').format(
                         m_type, m_uid))
            self._type_table[m_type]['uid'][m_uid] = new_index

        # Add to the name lookup table (if we have a name)
        if m_name:
            if m_name not in self._type_table[m_type]['name']:
                self._type_table[m_type]['name'][m_name] = []
            self._type_table[m_type]['name'][m_name].append(new_index)

        # tree_entry is now the final node in the tree
        tree_entry.metadata_index = new_index

    def _lookup_by_keyval(self, locator):
        """
        Attempts to lookup a metadata object by locator information.
        This information is based either on a type/name pair or a
        type/uid pair. Extra information passed as part of a locator
        can be identified based on user-defined functions.

        Args:
        -----
        locator: A dictionary containing a 'type' key, as well as
            either a 'name' or 'uid' key. Extra key-value pairs
            will be identified based on user-defined functions.

        Returns:
        --------
        A metadata object referenced by the locator.

        Raises:
        -------
        A MetadataLookupError if the specified metadata does not exist.
        A RuntimeError if the locator does not include the correct
            keys.
        """
        # Do an initial check to make sure the locator is sane
        if 'type' not in locator:
            raise InconsistentMetadataError("Locator" +
                                            " does not include" +
                                            " the required 'type' key!")
        if 'name' not in locator and 'uid' not in locator:
            error_msg = ("Locator must include either the 'name' or 'uid'" +
                         " key, but is missing both!")
            raise InconsistentMetadataError(error_msg)
        if locator['type'] in self._type_table:
            lookup = self._type_table[locator['type']]
            if 'uid' in locator and locator['uid'] in lookup['uid']:
                return lookup['uid'][locator['uid']]
            if 'name' in locator and locator['name'] in lookup['name']:
                matches = lookup['name'][locator['name']]
                if len(matches) > 1:
                    # Not a unique lookup
                    error_str = ('Nonunique locator specification: ' +
                                 ' multiple metadata objects exist ' +
                                 'with type={}, name={}').format(
                                     locator['type'], locator['name'])
                    raise MetadataLookupError(error_str)
                return matches[0]
        raise MetadataLookupError('No metadata object found with ' +
                                  'given locator')

    def lookup_by_keyval(self, locator):
        """
        Attempts to look up a metadata object by locator information.
        This information is based either on a type/name pair or a
        type/uid pair. Extra information passed as part of the
        locator can be identified based on user-defined functions.

        Args:
        -----
        locator: A dictionary containing a 'type' key, as well as
            either a 'name' or 'uid' key. Extra key-value pairs
            will be identified based on user-defined functions.

        Returns:
        --------
        A metadata object referenced by the locator.

        Raises:
        -------
        A MetadataLookupError if the specified metadata does not exist.
        A RuntimeError if the locator does not include the correct
            keys.
        """
        return self._cache[self._lookup_by_keyval(locator)]

    def _lookup_by_filename(self, filename):
        """
        Internal method to lookup metadata by filename,
        returning a cache index.

        Args:
        -----
        filename: A Path specifying the piece of metadata to load.
            The filename is specified relative to the root.

        Returns:
        --------
        An integer giving the index of the metadata in self._cache

        Raises:
        -------
        A MetadataLookupError if the specified file does not exist.
        """
        # Check that the file exists
        if not (self.root_dir / filename).is_file():
            raise MetadataLookupError('Specified metadata file does not exist!')
        # Because it is safe to call add_metadata on a previously
        # added piece of metadata, utilize this idempotenece!
        self.add_metadata(filename)
        # Lookup using the tree
        tree_entry = self._filename_tree
        for part in filename.parts:
            tree_entry = tree_entry.children[part]
        return tree_entry.metadata_index

    def lookup_by_filename(self, filename):
        """
        Looks up a piece of metadata by filename.

        Args:
        -----
        filename: A Path specifying the piece of metadata to load.
            The filename is specified relative to the root.

        Returns:
        --------
        A metadata object referenced from that file location.

        Raises:
        -------
        A MetadataLookupError if the specified file does not exist.
        """
        return self._cache[self._lookup_by_filename(filename)]

    def _find_filename_tree_node(self, tree_location):
        """
        Given a filename tree location, returns the MetadataTree
        object representing that path location.

        Args:
        -----
        tree_location: A path-like object of the search location,
            specified relative to the root directory.

        Returns:
        --------
        A MetadataTree object, or None if no matching location found.
        """
        if isinstance(tree_location, str):
            tree_location = Path(tree_location)

        tree_entry = self._filename_tree
        if tree_location is not None:
            for part in tree_location.parts:
                if part not in tree_entry.children:
                    return None # Path not found, or has no metadata loaded
                tree_entry = tree_entry.children[part]
        return tree_entry


    def validate_chain(self, tree_location=None, should_verify_files=True):
        """
        Verifies that all parent relationships for
        metadata loaded under the given tree location
        are valid, and that all referenced files are
        in place.

        When a tree location is not given,
        the entire tree under the root is validated.

        When passed a directory, parent information is
        validated for all metadata files under that directory.

        When passed a single file, parent information is
        only validated for that single file.


        Args:
        -----
        tree_location: A path-like object of the search location,
            specified relative to the root directory.
        should_verify_files: (Optional). If false, skips the file existence
            check.

        Raises:
        -------
        InconsistentMetadataError: If a parent
            relationshipo is invalid or
            if a tracked file does not exist.
        """
        validated = [False] * len(self._cache)

        tree_entry = self._find_filename_tree_node(tree_location)
        if tree_entry is None:
            return

        # BFS the tree to get initial entries to check
        file_queue = [tree_entry]
        meta_queue = []
        while len(file_queue) != 0:
            idx = file_queue[0].metadata_index
            if idx is not None:
                meta_queue.append(idx)
            file_queue.extend(file_queue[0].children.values())
            del file_queue[0]

        # Now that we're done BFSing the tree, start processing
        # metadata by verifying each parent.
        accum_errors = []
        while len(meta_queue) != 0:
            if validated[meta_queue[0]]:
                del meta_queue[0]
                continue
            metadata = self._cache[meta_queue[0]]
            if should_verify_files:
                verify_files(metadata)

            for parent in metadata.parent:
                try:
                    if isinstance(parent, str):
                        # Load by filename
                        abspath = metadata.filename.parent / Path(parent)
                        relpath = abspath.relative_to(self.root_dir)
                        parent_idx = self._lookup_by_filename(relpath)
                    else:
                        # Load by locator
                        parent_idx = self._lookup_by_keyval(parent)
                    meta_queue.append(parent_idx)
                except MetadataLookupError as err:
                    accum_errors.append(error_format.format_parent_error(
                        parent, str(err), metadata.filename))
                except InconsistentMetadataError as err:
                    accum_errors.append(error_format.format_parent_error(
                        parent, str(err), metadata.filename))
            validated[meta_queue[0]] = True
            del meta_queue[0]
        if len(accum_errors) > 0:
            raise InconsistentMetadataError('\n'.join(accum_errors))

def verify_files(metadata):
    """
    Given a piece of tracked Metadata, checks that all
    referenced files exist. To start, this checks if
    every string given is a file that exists relative
    to the directory that the metadata file is in.

    If this fails, this attempts to check if, using glob
    matching, there is at least one file found.

    Args:
    -----
    metadata: A Metadata object represent the object to check.

    Raises:
    -------
    InconsistentMetadataError: If a referenced file does not exist.
    """

    our_dir = metadata.filename.parent
    for filename in metadata.files:
        try:
            if (our_dir / filename).exists():
                continue
        except OSError:
            pass # Could be invalid glob
        if len(list(our_dir.glob(filename))) > 0:
            continue
        error = ('For metdata object {}, specified tracked file {}' +
                 'does not exist.').format(str(metadata.filename), filename)
        raise InconsistentMetadataError(error)

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
        r_path = Path.cwd()
    else:
        r_path = Path(path)

    try:
        if r_path.is_dir():
            current_dir = r_path
        else:
            current_dir = r_path.parent

        # Resolve to an absolute path
        current_dir = current_dir.resolve()
        while not (current_dir / 'tame.yaml').is_file():
            up_dir = current_dir.parent
            # Make sure we didn't reach the filesystem root
            if up_dir == current_dir:
                raise UntrackedRepositoryError("No root 'tame.yaml' file found")
            # otherwise, continue searching
            current_dir = up_dir
        return str(current_dir / 'tame.yaml')
    except PermissionError as error:
        print(error)
        raise UntrackedRepositoryError("No root 'tame.yaml' found due to permission denied error")

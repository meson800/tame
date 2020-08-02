"""
Includes base code that is responsible for searching
attached metadata files, in addition to layout a framework
for users to define their own custom matchers if the
built-in is not sufficent.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
import enum
import fnmatch
import re
import operator

import dateparser

class MatchType(enum.Enum):
    """
    This enum can be used in a BaseMatcher
    to define how keyvalue pairs are matched.

    The default, `Equal`, checks for equality.
    For string values, implicit wildcards
    can be present before/after the string,
    as well as directly embedded inside.

    Less, LessEqual, Greater, and GreaterEqual
    implement <, <=, >, >=, and are valid for
    number or datetime types.

    Regex allows arbtirary regexes to
    be used for searching, instead of simple
    wildcard equality.
    """
    Equal = 1
    Less = 2
    LessEqual = 3
    Greater = 4
    GreaterEqual = 5
    Regex = 6

def try_date_number_load(value):
    """
    Attempts to interpret a value as a datetime, then as
    a number, then finally as a string, returning
    the converted value and a flag if it is a 'comparable'
    type, that is a datetime or a string

    Args:
    -----
    value: `str`: An input value to attempt conversion on.

    Returns:
    --------
    (converted_val, is_comparable). `converted_val` is the
    converted entry, and `is_comparable` is if the resulting
    time is comparable
    """
    try:
        convert_val = dateparser.parse(value)
    except ValueError:
        convert_val = None

    if convert_val is not None:
        return (convert_val, True)
    try:
        convert_val = float(value)
    except ValueError:
        convert_val = None

    if convert_val is not None:
        return (convert_val, True)
    return (convert_val, False)

class BaseMatcher: # pylint: disable=too-few-public-methods
    """
    A stub base class from which other matchers can be derived.
    Inherited classes should define the `matches` function,
    which takes a Metadata object and a parent_keyvals dictionary,
    which represents all parent-included keyvals.
    """

    def matches(self, metadata, parent_keyvals): # pylint: disable=unused-argument, no-self-use
        """
        Override this function in derived matchers.

        Checks if the specified piece of metadata
        matches. For BaseMatcher, this does a
        semi-intelligent matching that matches
        regexes, datetime ranges, and other basic
        behavior. This function should be defined
        in any custom user classes that extend BaseMatcher.

        Args:
        -----
        metadata: A Metadata object to search.
        parent_keyvals: A nested dictionary of keyvals to
            additionally search for matches.

        Returns:
        --------
        A boolean True if the metadata matches, False otherwise.
        """
        return False



class SimpleMatcher(BaseMatcher): # pylint: disable=too-few-public-methods
    """
    This matcher attempts to be fairly smart about how it searches;
    it does things like allowing range matching, date parsing,
    and so on.

    Inherited classes should define the `matches` function,
    which takes a Metadata object and a parent_keyvals dictionary,
    which represents all parent-included keyvalues.
    """
    def __init__(self, key, value,
                 include_parents=True, match_type=MatchType.Equal):
        """
        Initalizes the BaseMatcher with the internal
        information required to search metadata objects.

        When passed a key/value pair under the default
        equality comparison, it checks if the given
        keyvalue pair exists. The value is implicitly
        extended with wildcards on both sides in normal
        text mode. Extra wildcards can be added with *.

        When the key passed is None, all keyvalue pairs
        are searched.

        Args:
        -----
        key: A string describing a key to search for, or None.
            If key is None, then any keyvalue pair is matched.
        value: A string encoding the value to look for. This string
            will be attempted to be parsed as a datetime and number,
            before defaulting back to a string.
        include_parents: A boolean stating if parent keyvalues should
            be considered.
        match_type: A MatchType indicating which match mode should be
            used. Equal can be used for all value types, whereas
            Less, LessEqual, Greater, GreaterEqual can only
            be used with datetimes and numbers. Regex can be used
            with strings to bypass the simple wildcard matching
            used for Equal.

        Returns:
        --------
        An initalized SimpleMatcher
        """
        self._key = key
        self._include_parents = include_parents
        self._match_type = match_type

        self._value, self._val_is_comparable = try_date_number_load(value)

        if self._match_type == MatchType.Equal:
            # Generate regex
            self._regex = fnmatch.translate('*{}*'.format(value))
        else:
            self._regex = value

        if not self._val_is_comparable and (
                self._match_type == MatchType.Less or
                self._match_type == MatchType.LessEqual or
                self._match_type == MatchType.Greater or
                self._match_type == MatchType.GreaterEqual):
            error_msg = 'Requsted ordering lookup {}, but value '
            error_msg += '{} cannot be interpreted as a date or number'
            raise ValueError(error_msg.format(self._match_type, value))
        self._matcher_func = self._generate_matcher_func()

    def _generate_matcher_func(self):
        """
        Generates a matcher function, given the different search types set
        by the constructor.

        Returns:
        --------
        A function that takes a single argument, a value to match against.
        """
        def regex_matcher(to_match_val):
            matches = re.match(self._regex, to_match_val)
            return matches is not None

        def simple_matcher(to_match_val, operator_func):
            matching_val = try_date_number_load(to_match_val)
            try:
                return operator_func(self._value, matching_val)
            except TypeError:
                return False

        simple_regex_match = (self._match_type == MatchType.Equal
                              and not self._val_is_comparable)

        if simple_regex_match or self._match_type == MatchType.Regex:
            # Just use regex matching
            return regex_matcher
        # No elif required, as we return out of these functions
        if self._match_type == MatchType.Equal:
            return lambda val: simple_matcher(val, operator.eq)
        if self._match_type == MatchType.Less:
            return lambda val: simple_matcher(val, operator.lt)
        if self._match_type == MatchType.LessEqual:
            return lambda val: simple_matcher(val, operator.le)
        if self._match_type == MatchType.Greater:
            return lambda val: simple_matcher(val, operator.gt)
        if self._match_type == MatchType.GreaterEqual:
            return lambda val: simple_matcher(val, operator.ge)
        raise ValueError('Unable to create a matcher function for given arguments!')


    def matches(self, metadata, parent_keyvals):
        """
        Checks if the specified piece of metadata
        matches. For BaseMatcher, this does a
        semi-intelligent matching that matches
        regexes, datetime ranges, and other basic
        behavior. This function should be defined
        in any custom user classes that extend BaseMatcher.

        Args:
        -----
        metadata: A Metadata object to search.
        parent_keyvals: A nested dictionary of keyvals to
            additionally search for matches.

        Returns:
        --------
        A boolean True if the metadata matches, False otherwise.
        """

        search_dict = {'type': metadata.type, 'name': metadata.name,
                       'uid': metadata.uid, **metadata.data}

        # Now that we have our matcher function, recursively check for a match
        # in our dictionaries. If we find a list, check each list item
        dicts_to_process = [search_dict]
        if self._include_parents:
            dicts_to_process.append(parent_keyvals)

        while len(dicts_to_process) > 0:
            searcher = dicts_to_process[0]
            for key, val in searcher:
                if self._key is None or key == self._key:
                    # Search these values
                    for item in val if isinstance(val, list) else [val]:
                        if self._matcher_func(item):
                            return True
                if isinstance(val, dict):
                    dicts_to_process.append(val)
                # Cleanup dictionary queue
                del dicts_to_process[0]
        # Nothing matched, return false
        return False

class AndMatcher(BaseMatcher): # pylint: disable=too-few-public-methods
    """
    A simple helper class that only matches if
    all of the matchers passed match the piece
    of metadata.
    """
    def __init__(self, *matchers):
        """
        Takes matchers to be ANDed together as variable
        arguments. If you have a list of matchers to AND
        together, you can expand them as `AndMatcher(*list_of_matchers)`.

        Args:
        -----
        *matchers: A variable number of matchers to AND together. If no
            arguments are passed, this matcher always returns True when
            called on any piece of metadata.

        Returns:
        --------
        An initalized AndMatcher
        """
        self._matchers = list(matchers)

    def matches(self, metadata, parent_keyvals):
        """
        Returns a valid match if all underlying matchers return true.

        Args:
        -----
        metadata: A Metadata object to search.
        parent_keyvals: A nested dictionary of parent keyvals.

        Returns:
        --------
        Boolean True if all submatchers match, False if any of the submatchers
        do not match.
        """
        all_match = True
        for matcher in self._matchers:
            if not matcher.matches(metadata, parent_keyvals):
                all_match = False
        return all_match

class OrMatcher(BaseMatcher): # pylint: disable=too-few-public-methods
    """
    A simple helper class that matches if
    any of the matchers passed match the piece
    of metadata.
    """
    def __init__(self, *matchers):
        """
        Takes matchers to be ORed together as variable
        arguments. If you have a list of matchers to OR
        together, you can expand them as `OrMatcher(*list_of_matchers)`.

        Args:
        -----
        *matchers: A variable number of matchers to OR together. If no
            arguments are passed, this matcher always returns True when
            called on any piece of metadata.

        Returns:
        --------
        An initalized OrMatcher
        """
        self._matchers = list(matchers)

    def matches(self, metadata, parent_keyvals):
        """
        Returns a valid match if any of the underlying matchers return true.

        Args:
        -----
        metadata: A Metadata object to search.
        parent_keyvals: A nested dictionary of parent keyvals.

        Returns:
        --------
        Boolean True if any submatchers matches.
        """
        if len(self._matchers) == 0:
            return True

        for matcher in self._matchers:
            if matcher.matches(metadata, parent_keyvals):
                return True
        return False

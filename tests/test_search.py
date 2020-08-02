from pathlib import Path
import pytest

import tame.core
from tame.search import SimpleMatcher, MatchType

from test_helpers import touch, init_cache

def test_simple_matcher(tmpdir):
    """Verifies that all functionality of the SimpleMatcher works.
    This includes number matching, date matching, and simple/regex
    text matching.
    """
    t, cache = init_cache(tmpdir)

    with open(str(t / 'meta1.yaml'), 'w') as f:
        f.write("""
        type: search_test
        name: meta_name
        uid: meta_uid

        list_keyval:
          - a_list_key_1
          - a_list_key_2
          - a_funky_list_item

        nested_dict_test:
          - simple_standalone_item
          - internal_nested_dict:
              internal_key: an_internal_val
              another_internal_key: meaning_of_life

        some_numbers: 3.45
        some_dates:
          - 2020-05-02
          - 2020-07-01
          - 1990-01-01
        """)
    cache.add_metadata(Path('meta1.yaml'))
    cache.validate_chain()
    meta = cache.lookup_by_filename(Path('meta1.yaml'))

    test_anykey_match = SimpleMatcher(None, 'meaning_of_life')
    assert test_anykey_match.matches(meta, {})

    type_match = SimpleMatcher('type', 'search_test')
    assert type_match.matches(meta, {})
    uid_mismatch = SimpleMatcher('uid', 'invalid')
    assert not uid_mismatch.matches(meta, {})

    test_simple_list_match = SimpleMatcher('list_keyval', 'list_key')
    assert test_simple_list_match.matches(meta, {})

    test_regex_list_match = SimpleMatcher('list_keyval',
                                          'a_list_key_\\d',
                                          match_type = MatchType.Regex)
    assert test_regex_list_match.matches(meta, {})

    test_nested_dict_match = SimpleMatcher('another_internal_key', 'meaning')
    assert test_nested_dict_match.matches(meta, {})

    test_number_match = SimpleMatcher('some_numbers', '3.2',
                                      match_type = MatchType.Greater)
    assert test_number_match.matches(meta, {})

    test_number_less_match = SimpleMatcher('some_numbers', '5',
                                           match_type = MatchType.Less)
    assert test_number_less_match.matches(meta, {})

    test_number_le_match = SimpleMatcher('some_numbers', '3.45',
                                         match_type = MatchType.LessEqual)
    assert test_number_le_match.matches(meta, {})
    test_number_ge_match = SimpleMatcher('some_numbers', '3.45',
                                         match_type = MatchType.GreaterEqual)
    assert test_number_ge_match.matches(meta, {})

    test_date_match = SimpleMatcher('some_dates', '2020-07-01')
    assert test_date_match.matches(meta, {})

    test_date_ineq_match = SimpleMatcher('some_dates', '2020-06-01',
                                         match_type = MatchType.Greater)
    assert test_date_match.matches(meta, {})

    test_date_ineq_invalid = SimpleMatcher('some_dates', '2020-12-01',
                                           match_type = MatchType.GreaterEqual)
    assert not test_date_ineq_invalid.matches(meta, {})

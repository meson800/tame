from pathlib import Path
import pytest

import tame.core

from test_helpers import touch

def generate_scc_files_and_cache(t, num_nodes, node_dict):
    """
    Generates nearly empty metadata files that have
    the desired graph structure.
    
    Args:
    -----
    t: a Path object encoding the temporary directory
    num_nodes: integer, the number of nodes to create (indexed from 0)
    node_dict: A dictionary, where keys are node ID and values are
        a list of parent nodes.

    Returns:
    --------
    The return value of calculate_scc, a lookup dict and a list of SCC tuples.
    """
    touch(t / 'tame.yaml')
    cache = tame.core.MetadataCache(t / 'tame.yaml')
    for i in range(num_nodes):
        with open(str(t / 'meta{}.yaml'.format(i)), 'w') as f:
            f.write('type: graph_test\nname: meta{}\n\n'.format(i))
            # Write parent connections
            if i in node_dict and len(node_dict[i]) > 0:
                f.write('parent:\n')
                for parent in node_dict[i]:
                    f.write('  - {{type: graph_test, name: meta{}}}\n'.format(parent))
        cache.add_metadata(str(t / 'meta{}.yaml'.format(i)))
    
    cache.validate_chain()
    return cache._calculate_scc()

def test_scc_generation(tmpdir):
    """
    Checks that our implementation of Tarjan's algorithm
    properly identifies all of the strongly connected
    components.
    """
    t = Path(tmpdir.strpath)
    scc = generate_scc_files_and_cache(t, 5, {
            0: [1],
            1: [2, 4],
            2: [3],
            3: [1]})

    assert (0,) in scc[1]
    assert (1,2,3) in scc[1]
    assert (4,) in scc[1]

def test_nested_cycles(tmpdir):
    """
    Verifies that the algorithm properly handles
    cycles within cycles.
    """
    t = Path(tmpdir.strpath)
    scc = generate_scc_files_and_cache(t, 5, {
            0: [1],
            1: [2, 3],
            2: [1],
            3: [4],
            4: [0]})
    assert len(scc[1]) == 1
    for val in scc[0].values():
        assert val == 0

def test_scc_return_val_coorespondance(tmpdir):
    """
    Verifies that the SCC mapping dictionary and list of SCCs match up
    """
    t = Path(tmpdir.strpath)
    scc = generate_scc_files_and_cache(t, 8, {
            0: [1],
            1: [2],
            2: [0],
            3: [4],
            4: [5],
            5: [6],
            6: [7],
            7: [6]})
    assert (0,1,2) in scc[1]
    assert (3,) in scc[1]
    assert (4,) in scc[1]
    assert (5,) in scc[1]
    assert (6,7) in scc[1]

    for i, comp in enumerate(scc[1]):
        for node in comp:
            assert scc[0][node] == i

def test_empty_graph(tmpdir):
    """
    Verifies that calculate_scc works on an empty graph
    """
    t = Path(tmpdir.strpath)
    scc = generate_scc_files_and_cache(t, 0, {})
    assert len(scc[0]) == 0
    assert len(scc[1]) == 0

def test_singleton_graph(tmpdir):
    """
    Verifies that a graph with no parents is also processed correctly.
    """
    t = Path(tmpdir.strpath)
    num_nodes = 50
    scc = generate_scc_files_and_cache(t, num_nodes, {})
    
    for i in range(num_nodes):
        assert (i,) in scc[1]
        assert scc[0][i] == scc[1].index((i,))

def test_complete_graph(tmpdir):
    """
    Verifies that a maximally-dense graph is processed properly.
    """
    t = Path(tmpdir.strpath)
    num_nodes = 20
    scc = generate_scc_files_and_cache(t, num_nodes,
            {i: [j for j in range(num_nodes) if j != i] for i in range(num_nodes)})
    assert len(scc[1]) == 1
    cycle = set(scc[1][0])

    for i in range(num_nodes):
        assert i in cycle

def test_self_reference(tmpdir):
    """
    Verifies that a self-parent reference doesn't break.
    """
    t = Path(tmpdir.strpath)
    scc = generate_scc_files_and_cache(t, 3, {
            0: [1],
            1: [2],
            2: [2]})
    assert (0,) in scc[1]
    assert (1,) in scc[1]
    assert (2,) in scc[1]

def test_kv_empty_graph(tmpdir):
    """
    Verifies that calculate_scc_parent_keyvals properly handles
    an empty graph
    """
    t = Path(tmpdir.strpath)
    touch(t / 'tame.yaml')
    cache = tame.core.MetadataCache(t / 'tame.yaml')
    scc_kv = cache.calculate_scc_parent_keyvals()
    assert len(scc_kv[0]) == 0
    assert len(scc_kv[1]) == 0

def test_kv_tree(tmpdir):
    """
    Verifies that simple tree inheritance works
    """
    t = Path(tmpdir.strpath)
    touch(t / 'tame.yaml')
    cache = tame.core.MetadataCache(t / 'tame.yaml')

    with open(str(t / 'meta0.yaml'), 'w') as f:
        f.write("""
        type: kv_test
        name: meta0

        parent:
          - {type: kv_test, name: meta1}

        foo: bar1
        """)
    with open(str(t / 'meta1.yaml'), 'w') as f:
        f.write("""
        type: kv_test
        name: meta1

        parent:
          - {type: kv_test, name: meta2}

        foo: overlapping_key2
        baz: new_key
        """)
    with open(str(t / 'meta2.yaml'), 'w') as f:
        f.write("""
        type: kv_test
        name: meta2

        foo: another_overlap
        baz: new_key_overlap
        foobar: A third key approaches
        """)

    for i in range(3):
        cache.add_metadata('meta{}.yaml'.format(i))
    cache.validate_chain()
    scc_kv = cache.calculate_scc_parent_keyvals()

    # Zeroth key depends on both keys above it
    assert scc_kv[1][scc_kv[0][0]] == {
            ('kv_test', 'meta1', ''): {
                'foo': 'overlapping_key2',
                'baz': 'new_key'},
            ('kv_test', 'meta2', ''): {
                'foo': 'another_overlap',
                'baz': 'new_key_overlap',
                'foobar': 'A third key approaches'}}
    # First key just dpends on meta2
    assert scc_kv[1][scc_kv[0][1]] == {
            ('kv_test', 'meta2', ''): {
                'foo': 'another_overlap',
                'baz': 'new_key_overlap',
                'foobar': 'A third key approaches'}}
    # Last key doesn't depend on anything
    assert scc_kv[1][scc_kv[0][2]] == {}

def test_kv_cycle(tmpdir):
    """
    Ensures that cycles are properly handled, in that their keys
    are properly tradcked, along with the rest of the SCC graph.
    """
    t = Path(tmpdir.strpath)
    touch(t / 'tame.yaml')
    cache = tame.core.MetadataCache(t / 'tame.yaml')

    with open(str(t / 'meta0.yaml'), 'w') as f:
        f.write("""
        type: kv_test
        name: meta0

        parent:
          - {type: kv_test, name: meta1}
        foo: bar0
        """)
    with open(str(t / 'meta1.yaml'), 'w') as f:
        f.write("""
        type: kv_test
        name: meta1

        parent:
          - {type: kv_test, name: meta2}
          - {type: kv_test, name: meta3}
        foo: bar1
        """)
    with open(str(t / 'meta2.yaml'), 'w') as f:
        f.write("""
        type: kv_test
        name: meta2

        parent:
          - {type: kv_test, name: meta1}
          - {type: kv_test, name: meta4}
        foo: bar2
        """)
    with open(str(t / 'meta3.yaml'), 'w') as f:
        f.write("""
        type: kv_test
        name: meta3

        foo: bar3
        """)
    with open(str(t / 'meta4.yaml'), 'w') as f:
        f.write("""
        type: kv_test
        name: meta4

        foo: bar4
        """)
    for i in range(5):
        cache.add_metadata('meta{}.yaml'.format(i))
    cache.validate_chain()
    scc_kv = cache.calculate_scc_parent_keyvals()

    # Meta objects 0, 1, and 2 all depend on all of 1/2/3/4
    for i in range(3):
        assert scc_kv[1][scc_kv[0][i]] == {
                ('kv_test', 'meta1', ''): {
                    'foo': 'bar1'},
                ('kv_test', 'meta2', ''): {
                    'foo': 'bar2'},
                ('kv_test', 'meta3', ''): {
                    'foo': 'bar3'},
                ('kv_test', 'meta4', ''): {
                    'foo': 'bar4'}}
    # 3 and 4 don't depend on anything
    assert scc_kv[1][scc_kv[0][3]] == {}
    assert scc_kv[1][scc_kv[0][4]] == {}


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
    return cache.calculate_scc()

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

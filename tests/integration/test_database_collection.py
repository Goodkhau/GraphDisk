from pathlib import Path

import pytest

from src.disk_graph import Graph

@pytest.mark.pysqlite3_integration
def test_collection_class(metadata: dict[str, str], cleanUp: Path):
    graphs_folder = cleanUp
    name = metadata['scenario']

    graph = Graph(name=name, graphs_folder=graphs_folder)
    collection = graph.createCollection()

    node_one = graph.createNode({})
    node_two = graph.createNode({})
    node_three = graph.createNode({})

    assert collection.has(node_one) == False, "collection should not have first ptr"
    assert collection.has(node_two) == False, "collection should not have second ptr"
    assert collection.has(node_three) == False, "collection should not have third ptr"

    _ = collection.add(node_one).add(node_two)
    assert collection.has(node_one) == True, "collection should have first ptr"
    assert collection.has(node_two) == True, "collection should have second ptr"
    assert collection.has(node_three) == False, "collection should not have third ptr"
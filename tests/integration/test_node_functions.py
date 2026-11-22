import pytest

from pathlib import Path

from src.disk_graph import ColumnType, Graph

@pytest.mark.integration
def test_chain_adding_children(cleanUp: Path, metadata: dict[str, str]):
    graphs_folder = cleanUp
    name = metadata['scenario']

    graph = Graph(name=name, graphs_folder=graphs_folder)

    (
        children := graph.createNode({})
            .add(graph.createNode({}))
            .add(graph.createNode({}))
            .add(graph.createNode({}))
            .children()
    )

    parent_id = 1
    num_children = 3

    assert len(children) == num_children, "three children should exist"
    for i in range(num_children):
        child = children[i]
        assert child.value().get('id') == parent_id+i+1, "id should be auto incrementing"
        
        parents = child.parents()
        assert len(parents) == 1, "every child should have one parent"
        assert parents[0].value().get('id') == parent_id, "parent should be our expected id"

@pytest.mark.integration
def test_nested_children(cleanUp: Path, metadata: dict[str, str]):
    graphs_folder = cleanUp
    name = metadata['scenario']

    graph = Graph(name=name, graphs_folder=graphs_folder)

    (
        node := graph.createNode({})
            .add(graph.createNode({})
                .add({}))
            .add(graph.createNode({})
                .add({})
                .add({}))
            .add(graph.createNode({})
                .add({})
                .add({})
                .add({}))
    )

    root_id = 1
    num_children_first_layer = 3
    children = node.children()
    assert len(children) == num_children_first_layer, "there should be three children"
    for i in range(num_children_first_layer):
        child = children[i]

        parents = child.parents()
        assert len(parents) == 1, "every child should have one parent"
        assert parents[0].value().get('id') == root_id, "root id should be our expected id"

        grand_children = child.children()
        assert len(grand_children) == i+1, "assert expected children are created"
        for grand_child in grand_children:
            parents_of_grand = grand_child.parents()
            assert len(parents_of_grand) == 1, "grand childs should have one parent"
            assert child == parents_of_grand[0], "child and parent of grand child should match"

@pytest.mark.integration
def test_duplicate_connection(cleanUp: Path, metadata: dict[str, str]):
    graphs_folder = cleanUp
    name = metadata['scenario']

    graph = Graph(name=name, graphs_folder=graphs_folder)

    node_one = graph.createNode({})
    node_two = graph.createNode({})

    _ = node_one.add(node_two).add(node_two)
    _ = node_one.add(node_two)

    children = node_one.children()
    assert len(children) == 1, "node one should only have one child"
    assert node_two == children[0], "the child should be node two"

    parents = node_two.parents()
    assert len(parents) == 1, "node tow should only have one parent"
    assert node_one == parents[0], "the parent should be node one"

@pytest.mark.integration
def test_chaining_connect(cleanUp: Path, metadata: dict[str, str]):
    graphs_folder = cleanUp
    name = metadata['scenario']

    graph = Graph(name=name, graphs_folder=graphs_folder).updateConfigFile({
        "index": ColumnType.Integer.name
    })

    head = graph.createNode({"index": 0})

    (
        last := head
            .connect({"index": 1})
            .connect({"index": 2})
            .connect({"index": 3})
            .connect({"index": 4})
    )

    current = 0
    curr_node = head
    while curr_node != last:
        assert curr_node.value().get("index") == current, "current node should be the correct index"
        current += 1
        curr_node = curr_node.children()[0]
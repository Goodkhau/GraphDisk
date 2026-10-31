import pytest
import json

from src.disk_graph import Graph
from src.disk_graph.db.pysqlite3.interface import ColumnType

@pytest.mark.integration
def test_chain_adding_children(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']
    config_path = graphs_folder / name / "config.json"

    graph = Graph(name=name, graphs_folder=graphs_folder)

    (
        children := graph.createNode()
            .add(graph.createNode())
            .add(graph.createNode())
            .add(graph.createNode())
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
def test_nested_children(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']
    config_path = graphs_folder / name / "config.json"

    graph = Graph(name=name, graphs_folder=graphs_folder)

    (
        node := graph.createNode()
            .add(graph.createNode()
                .add(graph.createNode()))
            .add(graph.createNode()
                .add(graph.createNode())
                .add(graph.createNode()))
            .add(graph.createNode()
                .add(graph.createNode())
                .add(graph.createNode())
                .add(graph.createNode()))
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
            assert child == grand_child.parents()[0], "child and parent of grand child should match"
import pytest
from disk_graph import Graph, ColumnType

@pytest.mark.e2e
def test_prefix_tree(case, metadata, default_teardown):
    data, output = case
    name = metadata['scenario']

    test_graph = Graph(name).updateConfigFile({
        "word": ColumnType.String.name,
        "layer": ColumnType.Integer.name
    })

    root_node = test_graph.createNode({"id": "root"})

    for string in data:
        curr = root_node

        words = string.split(' ')
        for index in range(len(words)):
            children = curr.children()
            next_node = next((child for child in (children if children is not None else []) if child.value().get('word') == words[index]), None)
            if next_node is None:
                curr.add({"word": words[index], "layer": index})

            curr = next((child for child in curr.children() if child.value().get('word') == words[index]), None)
    
    for node in test_graph.bfsGenerator(root_node):
        print(node.value())
    
    raise Exception()
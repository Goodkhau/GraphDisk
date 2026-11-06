import pytest
from disk_graph import Graph, ColumnType

@pytest.mark.e2e
def test_prefix_tree(case):
    data, output = case

    test_graph = Graph("Test").updateConfigFile({
        "layer": ColumnType.Integer.value
    })

    root_node = test_graph.createNode({"id: 'root'"})

    for string in data:
        curr = root_node

        words = string.split(' ')
        for index in range(len(words)):
            next_node = next((parent for parent in curr.parents() if parent.value().get('id') is words[index]), None)
            if next_node is None:
                next_node = curr.add({"id": words[index], "layer": i+1})

            curr = next_node
    
    for node in root_node.bfs():
        pass
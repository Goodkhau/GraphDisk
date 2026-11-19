import pytest
from disk_graph import Graph, ColumnType

@pytest.mark.e2e
def test_prefix_tree(case, metadata, default_teardown):
    data, output = case
    name = metadata['scenario']

    test_graph = Graph(name)

    test_graph.updateConfigFile(
        update_tables=True,
        new_config = {
            "word": ColumnType.String.name,
            "layer": ColumnType.Integer.name
        }
    )

    root_node = test_graph.createNode({"layer": 0})

    for string in data:
        curr = root_node

        words = string.split(' ')
        for index in range(len(words)):
            children = curr.children()
            next_node = next((child for child in (children if children is not None else []) if child.value().get('word') == words[index]), None)
            if next_node is None:
                curr.add({"word": words[index], "layer": index+1})

            curr = next((child for child in curr.children() if child.value().get('word') == words[index]), None)
    
    bfs_list = []
    for node in test_graph.bfsGenerator(root_node):
        val = node.value()
        bfs_list.append(f"Layer {val.get('layer')}: {val.get('word')}" if val.get('layer') else "root")
    
    assert output == bfs_list, "prefix trie BFS traversal should be as expected"
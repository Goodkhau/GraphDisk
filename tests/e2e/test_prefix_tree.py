import pytest

from collections.abc import Generator

from disk_graph import Graph, ColumnType

@pytest.mark.e2e
def test_prefix_tree(case: Generator[list[str]], metadata: dict[str, str], default_teardown: None):
    sentences, output = case
    name = metadata['scenario']
    _ = default_teardown

    test_graph = Graph(name).updateConfigFile(
        new_config = {
            "word": ColumnType.String,
            "layer": ColumnType.Integer
        }
    )

    root_node = test_graph.createNode({"layer": 0})

    for sentence in sentences:
        curr = root_node

        words = sentence.split(' ')
        for index in range(len(words)):
            children = curr.children()
            next_node = next((child for child in (children if children else []) if child.value().get('word') == words[index]), None)

            curr = next_node if next_node else curr.connect(to_node={"word": words[index], "layer": index+1})
    
    bfs_list: list[str] = []
    for node in test_graph.bfsGenerator(root_node):
        val = node.value()
        bfs_list.append(f"Layer {val.get('layer')}: {val.get('word')}" if val.get('layer') else "root")
    
    assert output == bfs_list, "prefix trie BFS traversal should be as expected"
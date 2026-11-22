# disk-graph

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Light weight package for creating graphs on disk with a simple interface.

## Features

- Create graphs using functional paradigms.
- Database design is abstracted away; create graphs without touching SQL.
- Zero dependencies.
- Fully typed and tested on Python 3.14+

## Installation

```bash
git clone https://github.com/Goodkhau/GraphDisk.git
cd my_project
pip install "path to GraphDisk folder"
```

## Quick start

```python
from disk_graph import Graph, ColumnType

str_graph = Graph(ColumnType.STRING)
```

## Usage

A slightly deeper example showing the most common real-world use case:

### Linked List
```python
graph = Graph(name="Linked List").updateConfigFile({
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
```

### Prefix Trie
```python
graph = Graph(name="Prefix Trie").updateConfigFile(
    new_config = {
        "word": ColumnType.String.name,
        "layer": ColumnType.Integer.name
    }
)

root_node = graph.createNode({"layer": 0})

for sentence in sentences:
    curr = root_node

    words = sentence.split(' ')
    for index in range(len(words)):
        children = curr.children()
        next_node = next((child for child in (children if children else []) if child.value().get('word') == words[index]), None)

        curr = next_node if next_node else curr.connect(to_node={"word": words[index], "layer": index+1})
```

### Nested Nodes
```python
graph = Graph(name="Nested")

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
```
Creates a graph with 6 leaf nodes and a root with 3 children

## Development

```bash
pip install -e ".[dev]"
pytest                    # run unit tests
nox -s e2e                # run end-to-end tests against a built wheel
```

## Contributing

Contributions are welcome. Please open an issue to discuss larger changes first, then submit a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
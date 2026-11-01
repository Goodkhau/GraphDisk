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
pip install disk-graph
```

For development:

```bash
git clone https://github.com/Goodkhau/GraphDisk.git
cd mypackage
pip install -e ".[dev]"
```

## Quick start

```python
from disk_graph import Graph, ColumnType

str_graph = Graph(ColumnType.STRING)
```

## Usage

A slightly deeper example showing the most common real-world use case:

```python
from mypackage import Client

client = Client(api_key="...")
data = client.fetch("something")
```

For full documentation, see the [docs](https://you.github.io/mypackage) or the [examples/](examples/) folder.

## Configuration

| Option | Default | Description |
|---|---|---|
| `timeout` | `30` | Request timeout in seconds |
| `retries` | `3` | Number of retry attempts |

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
import pytest
import json

from src.disk_graph import Graph

def updateConfig(path, config):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    with open(path, "w") as file:
        json.dump(config, file)

@pytest.mark.integration
def test_graph_creation(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']

    updateConfig(graphs_folder / name / "config.json", {
        "id": "TEXT"
    })
    graph = Graph(name=name, graphs_folder=graphs_folder)
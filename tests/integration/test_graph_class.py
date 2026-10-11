import pytest
import json

from src.disk_graph import Graph

def updateConfig(path, config):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    with open(path, "w") as file:
        json.dump(config, file)

def readConfig(path):
    try:
        with open(path, 'r', encoding="utf-8") as file:
            return json.load(file)
    except:
        return None

@pytest.mark.integration
def test_graph_creation(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']

    configs = {
        "id": "INTEGER",
        "test_col_1": "INTEGER",
        "test_col_2": "REAL",
        "test_col_3": "BLOB"
    }

    config_path = graphs_folder / name / "config.json"
    updateConfig(config_path, configs)

    graph = Graph(name=name, graphs_folder=graphs_folder)

    node_columns = graph.db.getTableColumns('node')
    assert len(node_columns) == len(configs), "the number of columns should match the provided config"

    for column in node_columns:
        conf_type = configs.get(column['name'])
        assert conf_type != None, "column should be derived from config"
        assert conf_type == column['type'], "column should match config"
    
    new_config = readConfig(config_path)
    assert new_config != None, "new config should exist"
    assert new_config == configs, "new config should match original config"

@pytest.mark.integration
def test_graph_invalid_config(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']

    configs = {
        "test_col_1": "BAD_TYPE",
        "test_col_2": "BAD_TYPE",
        "test_col_3": "BAD_TYPE"
    }

    config_path = graphs_folder / name / "config.json"
    updateConfig(config_path, configs)

    graph = Graph(name=name, graphs_folder=graphs_folder)

    node_columns = graph.db.getTableColumns('node')
    assert len(node_columns) == 1, "there should only be one column"
    assert node_columns[0]['name'] == "id", "only the default column 'id' should be created"
    assert node_columns[0]['type'] == "INTEGER", "default column type should be 'INTEGER'"
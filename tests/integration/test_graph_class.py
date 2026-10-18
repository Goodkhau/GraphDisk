import pytest
import json

from src.disk_graph import Graph, default_config
from src.disk_graph.db.pysqlite3.interface import ColumnType

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
        "id": ColumnType.Integer.name,
        "test_col_1": ColumnType.Integer.name,
        "test_col_2": ColumnType.Float.name,
        "test_col_3": ColumnType.Bytes.name
    }

    config_path = graphs_folder / name / "config.json"
    updateConfig(config_path, configs)

    graph = Graph(name=name, graphs_folder=graphs_folder)

    node_columns = graph.db.getTableColumns('node')
    assert len(node_columns) == len(configs), "the number of columns should match the provided config"

    for column in node_columns:
        conf_type = configs.get(column['name'])
        assert conf_type != None, "column should be derived from config"
        assert conf_type == ColumnType(column['type']).name, "column should match config"
    
    new_config = readConfig(config_path)
    assert new_config != None, "new config should exist"
    assert new_config.get('message') != None, "message should be attached to new config file"
    assert new_config == default_config | configs, "new config should match original config"

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

    new_config = readConfig(config_path)
    assert len(new_config) == 2, "there should only be one config updated with the default message"
    assert new_config.get('id') == ColumnType.Integer.name, f"the new config should have an id column that is default {ColumnType.Integer.name}"

@pytest.mark.integration
def test_graph_custom_node_pk(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']

    config_path = graphs_folder / name / "config.json"

    graph = Graph(name=name, node_pk_type=ColumnType.String.name, graphs_folder=graphs_folder)

    node_columns = graph.db.getTableColumns('node')
    assert len(node_columns) == 1, "there should only be one column"
    assert node_columns[0]['name'] == "id", "only the default column 'id' should be created"
    assert node_columns[0]['type'] == ColumnType.String.value, f"the column type should be the provided {ColumnType.String.value}"

    new_config = readConfig(config_path)
    assert len(new_config) == 2, "there should only be one config updated with the default message"
    assert new_config.get('id') == ColumnType.String.name, f"the new config should have an id column that is the provided {ColumnType.String.name}"

@pytest.mark.integration
def test_graph_mixed_config(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']

    configs = {
        "id": ColumnType.Integer.name,
        "test_col_1": ColumnType.Integer.name,
        "test_col_2": ColumnType.Float.name,
        "test_col_3": ColumnType.Bytes.name
    }

    config_path = graphs_folder / name / "config.json"
    updateConfig(config_path, configs)

    graph = Graph(name=name, graphs_folder=graphs_folder)

    configs = {
        "id": ColumnType.Integer.name,
        "test_col_1": ColumnType.Integer.name,
        "test_col_2": ColumnType.Float.name,
        "test_col_3": ColumnType.Bytes.name,
        "new_row": ColumnType.Integer.name
    }

    updateConfig(config_path, configs)
    graph.updateTables()

    node_columns = graph.db.getTableColumns('node')
    assert len(node_columns) == len(configs), "the number of columns should match the provided config"

    new_config = readConfig(config_path)
    assert new_config != None, "new config should exist"
    assert new_config == configs | default_config, "new config should match updated config with a message attached"


@pytest.mark.integration
def test_graph_retyping_unallowed(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']

    configs = {
        "id": ColumnType.Integer.name,
        "test_col_1": ColumnType.Integer.name,
        "test_col_2": ColumnType.Float.name,
        "test_col_3": ColumnType.Bytes.name
    }

    config_path = graphs_folder / name / "config.json"
    updateConfig(config_path, configs)

    graph = Graph(name=name, graphs_folder=graphs_folder)

    failed_configs = {
        "id": ColumnType.String.name,
        "test_col_1": ColumnType.Bytes.name,
        "test_col_2": ColumnType.Integer.name,
        "test_col_3": ColumnType.Float.name
    }

    updateConfig(config_path, configs)
    graph.updateTables()

    node_columns = graph.db.getTableColumns('node')
    assert len(node_columns) == len(configs), "the number of columns should match the original config"
    for column in node_columns:
        conf_type = configs.get(column['name'])
        assert conf_type != None, "column should be derived from config"
        assert conf_type == ColumnType(column['type']).name, "column should match config"

    new_config = readConfig(config_path)
    assert new_config != None, "new config should exist"
    assert new_config == configs | default_config, "new config should match updated config with a message attached"

@pytest.mark.integration
def test_graph_config_reinstated(cleanUp, metadata):
    graphs_folder = cleanUp
    name = metadata['scenario']

    configs = {
        "id": ColumnType.Integer.name,
        "test_col_1": ColumnType.Integer.name,
        "test_col_2": ColumnType.Float.name,
        "test_col_3": ColumnType.Bytes.name,
    }

    config_path = graphs_folder / name / "config.json"
    updateConfig(config_path, configs)

    graph = Graph(name=name, graphs_folder=graphs_folder)

    updateConfig(config_path, {})
    graph.updateTables()

    node_columns = graph.db.getTableColumns('node')
    assert len(node_columns) == len(configs), "the number of columns should match the original config"
    for column in node_columns:
        conf_type = configs.get(column['name'])
        assert conf_type != None, "column should be derived from config"
        assert conf_type == ColumnType(column['type']).name, "column should match config"

    new_config = readConfig(config_path)
    assert new_config != None, "new config should be created"
    assert new_config == configs | default_config, "new config should match original config with a message attached"
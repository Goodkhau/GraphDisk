import pytest
import random
import sqlite3

from src.disk_graph import Graph
from src.disk_graph.db.pysqlite3.interface import ColumnType

@pytest.mark.integration
def test_auto_incrementing(cleanUp, metadata, Config):
    graphs_folder = cleanUp
    name = metadata['scenario']
    config_path = graphs_folder / name / "config.json"

    configs = {
        "cust_field": ColumnType.String.name
    }

    Config.update(config_path, configs)
    graph = Graph(name, graphs_folder=graphs_folder)

    test_str = "test_str"
    num_rows = random.randint(1, 20)
    for _ in range(num_rows):
        graph.createNode({ "cust_field": test_str })

    rows = list(next(graph.getAllNodes()))

    assert len(rows) == num_rows, "the number of columns created should match what we created"
    for i in range(num_rows):
        assert rows[i].get("id") == i+1, "primary key should increment starting from 1"
        assert rows[i].get("cust_field") == test_str, "cust_field should be populated with test string"

@pytest.mark.integration
def test_auto_incrementing_passing_pk(cleanUp, metadata, Config):
    graphs_folder = cleanUp
    name = metadata['scenario']
    graph = Graph(name, graphs_folder=graphs_folder)

    first_segment = 13
    second_segment = 7
    nonincrementing_id = 113

    for _ in range(first_segment):
        graph.createNode()
    
    graph.createNode({ "id": nonincrementing_id })
    for _ in range(second_segment-1):
        graph.createNode()

    rows = list(next(graph.getAllNodes()))

    assert len(rows) == first_segment+second_segment, "the number of columns created should match what we created"
    for i in range(first_segment):
        assert rows[i]["id"] == i+1, "primary key should increment starting from 1"
    for i in range(second_segment):
        assert rows[first_segment+i].get("id") == nonincrementing_id+i, f"primary key should increment coninuing from {nonincrementing_id}"
    
@pytest.mark.integration
def test_integer_invalid_pk(cleanUp, metadata, Config):
    graphs_folder = cleanUp
    name = metadata['scenario']
    config_path = graphs_folder / name / "config.json"

    configs = {
        "cust_field": ColumnType.String.name
    }

    Config.update(config_path, configs)
    graph = Graph(name, graphs_folder=graphs_folder)

    invalid_pk = "invalid"
    valid_pk = "117"

    with pytest.raises(sqlite3.Error) as invalid_error:
        graph.createNode({ "id": invalid_pk })
    
    assert invalid_error.type is sqlite3.Error
    assert "Sqlite3Interface: Failed to insert column" in str(invalid_error.value), "exception should have message attached"

    node = graph.createNode({ "id": valid_pk })
    assert node.id == int(valid_pk), "string number should convert to number"

    rows = list(next(graph.getAllNodes()))
    assert len(rows) == 1, "there should be one row created"
    assert rows[0].get("id") == int(valid_pk), "node should be populated"

@pytest.mark.integration
def test_integer_duplicate_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_integer_bulk_nodes(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_empty_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_invalid_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_duplicate(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_bulk_nodes(cleanUp, metadata, Config):
    pass
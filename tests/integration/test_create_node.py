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
    for i in range(num_rows):
        node = graph.createNode({ "cust_field": test_str }).value()
        assert node.get('id') == i+1, "node object should be created with expected id"

    rows = list(next(graph.getAllNodesByPage()))

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

    for i in range(first_segment):
        node = graph.createNode().value()
        assert node.get('id') == i+1, "node object should be created with expected id"
    
    node = graph.createNode({ "id": nonincrementing_id }).value()
    assert node.get('id') == nonincrementing_id, "node object should be created with expected id"
    for i in range(second_segment-1):
        node = graph.createNode().value()
        assert node.get('id') == nonincrementing_id+i+1, "node object should be created with expected id"

    rows = list(next(graph.getAllNodesByPage()))

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

    graph = Graph(name, graphs_folder=graphs_folder)

    invalid_pk_str = "invalid"
    invalid_pk_byte = bytes([random.randint(0, 255) for _ in range(6)])
    valid_pk = "117"

    with pytest.raises(sqlite3.Error) as invalid_error_str:
        graph.createNode({ "id": invalid_pk_str })
    
    assert invalid_error_str.type is sqlite3.Error
    assert "Sqlite3Interface: Failed to insert column" in str(invalid_error_str.value), "exception should have message attached"

    with pytest.raises(sqlite3.Error) as invalid_pk_byte:
        graph.createNode({ "id": invalid_pk_str })
    
    assert invalid_pk_byte.type is sqlite3.Error
    assert "Sqlite3Interface: Failed to insert column" in str(invalid_pk_byte.value), "exception should have message attached"

    node = graph.createNode({ "id": valid_pk }).value()
    assert isinstance(node.get('id'), int), "string number should convert to number"
    assert node.get('id') == int(valid_pk), "string number should convert to number"

    rows = list(next(graph.getAllNodesByPage()))
    assert len(rows) == 1, "there should be one row created"
    assert isinstance(rows[0].get("id"), int), "column id should be string"
    assert rows[0].get("id") == int(valid_pk), "node should be populated"

@pytest.mark.integration
def test_integer_duplicate_pk(cleanUp, metadata, Config):
    graphs_folder = cleanUp
    name = metadata['scenario']
    config_path = graphs_folder / name / "config.json"

    graph = Graph(name, graphs_folder=graphs_folder, node_pk_type=ColumnType.String.name)

    duplicate_pk = "dupilcate"

    graph.createNode({ "id": duplicate_pk })
    with pytest.raises(sqlite3.Error) as invalid_error:
        graph.createNode({ "id": duplicate_pk })
    
    assert invalid_error.type is sqlite3.Error
    assert "Sqlite3Interface: Failed to insert column" in str(invalid_error.value), "exception should have message attached"

@pytest.mark.integration
def test_string_empty_pk(cleanUp, metadata, Config):
    graphs_folder = cleanUp
    name = metadata['scenario']
    config_path = graphs_folder / name / "config.json"

    graph = Graph(name, graphs_folder=graphs_folder, node_pk_type=ColumnType.String.name)

    empty_string = ""
    white_space = " \n\t"

    node = graph.createNode({ "id": empty_string }).value()
    assert node.get('id') == empty_string, "empty string should be accepted"

    node = graph.createNode({ "id": white_space }).value()
    assert node.get('id') == white_space, "white space id should be accepted"

    rows = list(next(graph.getAllNodesByPage()))
    assert len(rows) == 2, "both rows should be created and seperate"

    empty_string_row = next(row for row in rows if row.get("id") == empty_string)
    assert empty_string_row.get("id") == empty_string, "empty string should have a row"

    white_space_row = next(row for row in rows if row.get("id") == white_space)
    assert white_space_row.get("id") == white_space, "white space string should have a row"

@pytest.mark.integration
def test_string_invalid_pk(cleanUp, metadata, Config):
    graphs_folder = cleanUp
    name = metadata['scenario']
    config_path = graphs_folder / name / "config.json"

    graph = Graph(name, graphs_folder=graphs_folder, node_pk_type=ColumnType.String.name)

    invalid_pk = bytes([random.randint(0, 255) for _ in range(6)])
    valid_pk = 23

    with pytest.raises(sqlite3.Error) as invalid_error:
        graph.createNode({ "id": invalid_pk })
    
    assert invalid_error.type is sqlite3.Error
    assert "Sqlite3Interface: Failed to insert column" in str(invalid_error.value), "exception should have message attached"

    node = graph.createNode({ "id": valid_pk }).value()
    assert isinstance(node.get('id'), str), "string number should convert to string"
    assert node.get('id') == str(valid_pk), "string number should convert to string"

    rows = list(next(graph.getAllNodesByPage()))
    assert len(rows) == 1, "there should be one row created"
    assert isinstance(rows[0].get("id"), str), "string number should convert to string"
    assert rows[0].get("id") == str(valid_pk), "node should be populated"

@pytest.mark.integration
def test_byte_duplicate_pk(cleanUp, metadata, Config):
    pass

@pytest.mark.integration
def test_byte_invalid_pk(cleanUp, metadata, Config):
    pass
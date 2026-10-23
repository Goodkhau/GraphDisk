import pytest
import random

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

    num_rows = random.randint(1, 20)
    for _ in range(num_rows):
        graph.createNode()

    rows = list(next(graph.getAllNodes()))

    assert len(rows) == num_rows, "the number of columns created should match what we created"

@pytest.mark.integration
def test_auto_incrementing_passing_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_integer_invalid_pk(cleanUp, metadata, Config):
    pass
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
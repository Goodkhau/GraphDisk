import pytest
from pathlib import Path

from src.disk_graph.db.pysqlite3.interface import Sqlite3Interface, ColumnType

expected_rows = ['node', 'node_ptr', 'sqlite_sequence', 'edges', 'session', 'visited', 'deque']

@pytest.mark.pysqlite3_integration
def test_table_creation(cleanUp):
    graphs_folder = cleanUp
    name = "table_creation"
    (graphs_folder / name).mkdir()

    database = Sqlite3Interface(name, graphs_folder, ColumnType.Integer)

    assert set(database.getTables()) == set(expected_rows)
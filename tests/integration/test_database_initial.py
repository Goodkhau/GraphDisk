import pytest
from pathlib import Path

from src.disk_graph.db.pysqlite3.interface import Sqlite3Interface, ColumnType
from src.disk_graph.db.database_interface import database_interface

expected_rows = ['node', 'node_ptr', 'sqlite_sequence', 'edges', 'session', 'collection', 'deque']

@pytest.mark.pysqlite3_integration
def test_table_creation(cleanUp):
    graphs_folder = cleanUp
    name = "table_creation"
    (graphs_folder / name).mkdir()

    database: database_interface = Sqlite3Interface(name, graphs_folder, ColumnType.Integer)

    assert set(database.getTables()) == set(expected_rows)
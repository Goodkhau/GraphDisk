import pytest
from pathlib import Path

from src.disk_graph.db.pysqlite3 import Sqlite3Interface, ColumnType
from src.disk_graph.db.database_interface import database_interface

expected_rows = ['node', 'node_ptr', 'sqlite_sequence', 'edges', 'session', 'collection', 'deque']

@pytest.mark.integration
def test_table_creation(metadata: dict[str, str], cleanUp: Path):
    graphs_folder = cleanUp
    name = metadata['scenario']

    database: database_interface = Sqlite3Interface(name, graphs_folder, ColumnType.Integer)

    assert set(database.select_tables()) == set(expected_rows)
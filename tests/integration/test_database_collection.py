import pytest

from src.disk_graph.db.pysqlite3.interface import Sqlite3Interface, ColumnType

@pytest.mark.pysqlite3_integration
def test_collection_class(cleanUp):
    graphs_folder = cleanUp
    name = "collection"

    collection = Sqlite3Interface(name, graphs_folder, ColumnType.Integer).createCollection()

    node_ptr_1 = 1
    node_ptr_2 = 2
    node_ptr_3 = 3

    assert collection.has(node_ptr_1) == False, "collection should not have first ptr"
    assert collection.has(node_ptr_2) == False, "collection should not have second ptr"
    assert collection.has(node_ptr_3) == False, "collection should not have third ptr"

    collection.add(node_ptr_1).add(node_ptr_2)
    assert collection.has(node_ptr_1) == True, "collection should have first ptr"
    assert collection.has(node_ptr_2) == True, "collection should have second ptr"
    assert collection.has(node_ptr_3) == False, "collection should not have third ptr"
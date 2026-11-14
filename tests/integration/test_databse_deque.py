import pytest
from pathlib import Path

from src.disk_graph.db.pysqlite3.interface import Sqlite3Interface, ColumnType

@pytest.mark.pysqlite3_integration
def test_deque_push_back(cleanUp):
    graphs_folder = cleanUp
    name = "deque_push_back"

    node_ptr_1 = 1
    node_ptr_2 = 2

    database = Sqlite3Interface(name, graphs_folder, ColumnType.Integer)

    deque = database.createDeque()
    assert deque.empty() == True, "deque should initially be empty"
    assert deque.front() == None, "front position should be none"
    assert deque.back() == None, "back position should be none"

    deque.push_back(node_ptr_1)
    assert deque.empty() == False, "deque should not be empty"
    assert deque.front() == node_ptr_1, "front position should be 1"
    assert deque.back() == deque.front(), "back position should also be 1"

    deque.push_back(node_ptr_2)
    assert deque.empty() == False, "deque should not be empty"
    assert deque.front() == node_ptr_1, "front position should be 1"
    assert deque.back() == node_ptr_2, "back position should also be 2"

@pytest.mark.pysqlite3_integration
def test_deque_pop_front(cleanUp):
    graphs_folder = cleanUp
    name = "deque_pop_front"

    node_ptr_1 = 1
    node_ptr_2 = 2

    database = Sqlite3Interface(name, graphs_folder, ColumnType.Integer)
    deque = database.createDeque()

    deque.push_back(node_ptr_1)
    deque.push_back(node_ptr_2)

    assert deque.front() == deque.pop_front(), "popped value should be from the front"
    assert deque.front() == deque.pop_front(), "popped value should be from the front"

    assert deque.empty() == True, "deque should be empty"
    assert deque.pop_front() == None, "pop front should return None when deque is empty"
import pytest
from pathlib import Path

from src.disk_graph import Graph

@pytest.mark.pysqlite3_integration
def test_deque_push_back(metadata: dict[str, str], cleanUp: Path):
    graphs_folder = cleanUp
    name = metadata['scenario']

    graph = Graph(name, graphs_folder=graphs_folder)

    deque = graph.createDeque()

    node_one = graph.createNode({})
    node_two = graph.createNode({})

    assert deque.empty() == True, "deque should initially be empty"
    assert deque.front() == None, "front position should be none"
    assert deque.back() == None, "back position should be none"

    _ = deque.push_back(node_one)
    assert deque.empty() == False, "deque should not be empty"
    assert deque.front() == node_one, "front position should be 1"
    assert deque.back() == deque.front(), "back position should also be 1"

    _ = deque.push_back(node_two)
    assert deque.empty() == False, "deque should not be empty"
    assert deque.front() == node_one, "front position should be 1"
    assert deque.back() == node_two, "back position should also be 2"

@pytest.mark.pysqlite3_integration
def test_deque_pop_front(metadata: dict[str, str], cleanUp: Path):
    graphs_folder = cleanUp
    name = metadata['scenario']

    graph = Graph(name, graphs_folder=graphs_folder)
    deque = graph.createDeque()

    node_one = graph.createNode({})
    node_two = graph.createNode({})

    _ = deque.push_back(node_one).push_back(node_two)

    assert deque.front() == deque.pop_front(), "popped value should be from the front"
    assert deque.front() == deque.pop_front(), "popped value should be from the front"

    assert deque.empty() == True, "deque should be empty"
    assert deque.pop_front() == None, "pop front should return None when deque is empty"
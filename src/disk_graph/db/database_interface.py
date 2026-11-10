from abc import ABC, abstractmethod
from enum import Enum

class Edges(str, Enum):
    From    = "from_node_ptr"
    To      = "to_node_ptr"

class NodePtr(str, Enum):
    Node        = "node"
    InDegree    = "in_degree"
    OutDegree   = "out_degree"

class database_interface(ABC):
    class Deque:
        pass

    class Set:
        pass

    def __init__(self, name: str = ''):
        pass

    @abstractmethod
    def createTables(self):
        pass

    @abstractmethod
    def getTableColumns(self, name: str):
        pass

    @abstractmethod
    def createNodeColumns(self, new_columns: list[dict]):
        pass
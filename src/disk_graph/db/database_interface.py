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
    def insert_session(self, session_id: str):
        pass

    @abstractmethod
    def create_tables(self):
        pass

    @abstractmethod
    def select_tables(self):
        pass

    @abstractmethod
    def select_table_columns(self, name: str):
        pass

    @abstractmethod
    def alter_node_columns(self, new_columns: list[dict]):
        pass

    @abstractmethod
    def select_node(self, node_ptr, use_dict_fact):
        pass

    @abstractmethod
    def insert_node(self, row_data: dict):
        pass

    @abstractmethod
    def insert_edge(self, from_ptr, to_ptr, throw_on_duplicate):
        pass

    @abstractmethod
    def select_edge_to_ptr(self, from_node_ptr, use_dict_fact = True):
        pass

    @abstractmethod
    def select_edge_from_ptr(self, to_node_ptr, use_dict_fact = True):
        pass

    @abstractmethod
    def paginate_all_nodes(self, page_size, use_dict_fact):
        pass
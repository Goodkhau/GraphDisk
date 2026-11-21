from abc import ABC, abstractmethod
from enum import Enum
from typing import Literal, overload

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
    def select_tables(self) -> list[str]:
        pass

    @abstractmethod
    def select_table_columns(self, name: str) -> list[dict[str, str]]:
        pass

    @abstractmethod
    def alter_node_columns(self, new_columns: list[dict[str, str]]) -> tuple[list[str], list[str]]:
        pass

    @overload
    def select_node(self, node_ptr: int, use_dict_fact: Literal[True]) -> dict[str, str | int] | None: ...

    @overload
    def select_node(self, node_ptr: int, use_dict_fact: Literal[False]) -> tuple[str | int] | None: ...

    @abstractmethod
    def select_node(self, node_ptr: int, use_dict_fact: bool) -> dict[str, str | int] | tuple[str | int] | None:
        pass

    @abstractmethod
    def insert_node(self, row_data: dict[str, str | int]):
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
    
    @abstractmethod
    def insert_deque(self, position: int, node_ptr: int, session_id: str):
        pass

    @abstractmethod
    def select_deque_highest(self, session_id: str) -> tuple[int, int, int, str]:
        pass

    @abstractmethod
    def select_deque_lowest(self, session_id: str) -> tuple(int, int, int, str):
        pass

    @abstractmethod
    def delete_deque(self, position: int, session_id: str) -> tuple(int, int, int, str):
        pass

    @abstractmethod
    def count_deque(self, session_id: str):
        pass
from abc import ABC, abstractmethod
from collections.abc import Generator
from enum import Enum
from pathlib import Path
from typing import Any, Literal, NamedTuple, overload

class Edge(NamedTuple):
    id:             int
    from_node_ptr:  int
    to_node_ptr:    int

class NodePtr(str, Enum):
    Node        = "node"
    InDegree    = "in_degree"
    OutDegree   = "out_degree"

class database_interface(ABC):
    def __init__(self, name: str, graphs_folder: Path, node_pk_type: Any) -> None:  # pyright: ignore[reportAny, reportExplicitAny]
        pass

    @abstractmethod
    def insert_session(self, session_id: str) -> str:
        pass

    @abstractmethod
    def create_tables(self, node_pk_type: Any) -> None:  # pyright: ignore[reportExplicitAny, reportAny]
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
    def select_node(self, node_ptr: int, use_dict_fact: Literal[False]) -> tuple[int] | None: ...

    @abstractmethod
    def select_node(self, node_ptr: int, use_dict_fact: bool) -> dict[str, str | int] | tuple[int] | None:
        pass

    @abstractmethod
    def insert_node(self, row_data: dict[str, str | int]) -> int:
        pass

    @abstractmethod
    def insert_edge(self, from_ptr: int, to_ptr: int) -> int | None:
        pass

    @abstractmethod
    def select_edge_to_ptr(self, from_node_ptr: int) -> list[Edge]:
        pass

    @abstractmethod
    def select_edge_from_ptr(self, to_node_ptr: int) -> list[Edge]:
        pass

    @abstractmethod
    def paginate_all_node_ptr(self, page_size: int, use_dict_fact: bool) -> Generator[list[dict[str, str | int]] | tuple[tuple[str | int]]]:
        pass
    
    @abstractmethod
    def insert_deque(self, position: int, node_ptr: int, session_id: str) -> int:
        pass

    @abstractmethod
    def select_deque_highest(self, session_id: str) -> tuple[int, int, int, str] | None:
        pass

    @abstractmethod
    def select_deque_lowest(self, session_id: str) -> tuple[int, int, int, str] | None:
        pass

    @abstractmethod
    def delete_deque(self, position: int, session_id: str) -> tuple[int, int, int, str] | None:
        pass

    @abstractmethod
    def count_deque(self, session_id: str) -> int:
        pass

    @abstractmethod
    def select_collection(self, node_ptr: int, session_id: str) -> tuple[str | int] | None:
        pass

    @abstractmethod
    def insert_collection(self, node_ptr: int, session_id: str) -> int:
        pass
from dataclasses import dataclass
from typing import Literal, Self, overload

from src.disk_graph.db.database_interface import database_interface

@dataclass(order=True)
class Node:
    def __init__(self, node_ptr: int, db: database_interface):
        self.ptr: int = node_ptr
        self._db: database_interface = db
    
    @overload
    def value(self, use_dict_fact: Literal[False]) -> tuple[str | int]: ...
    @overload
    def value(self, use_dict_fact: Literal[True] = True) -> dict[str, str | int]: ...
    def value(self, use_dict_fact: bool = True) -> dict[str, str | int] | tuple[str | int]:
        node_row = self._db.select_node(self.ptr, use_dict_fact);
        if node_row is None:
            raise Exception(f"Failed to get Node from node_ptr: {self.ptr}")
        return node_row

    def add(self, to_node: dict[str, str | int] | Node) -> Self:
        if isinstance(to_node, Node):
            _ = self._db.insert_edge(from_ptr=self.ptr, to_ptr=to_node.ptr)
        else:
            new_node_ptr = self._db.insert_node(to_node)
            _ = self._db.insert_edge(from_ptr=self.ptr, to_ptr=new_node_ptr)

        return self
    
    def connect(self, to_node: dict[str, str | int] | Node) -> Node:
        if isinstance(to_node, Node):
            _ = self._db.insert_edge(from_ptr=self.ptr, to_ptr=to_node.ptr)
            to_node_ptr = to_node.ptr
        else:
            to_node_ptr = self._db.insert_node(to_node)
            _ = self._db.insert_edge(from_ptr=self.ptr, to_ptr=to_node_ptr)

        return Node(node_ptr=to_node_ptr, db=self._db)

    def children(self) -> list[Node]:
        return [Node(node_ptr=edge.to_node_ptr, db=self._db) for edge in self._db.select_edge_to_ptr(from_node_ptr=self.ptr)]

    def parents(self) -> list[Node]:
        return [Node(node_ptr=edge.from_node_ptr, db=self._db) for edge in self._db.select_edge_from_ptr(to_node_ptr=self.ptr)]
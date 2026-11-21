from dataclasses import dataclass

from src.disk_graph.db.database_interface import database_interface, Edges

@dataclass(order=True)
class Node:
    def __init__(self, node_ptr: int, db: database_interface):
        self.ptr: int = node_ptr
        self._db: database_interface = db
    
    def value(self, use_dict_fact = True):
        return self._db.select_node(self.ptr, use_dict_fact);

    def add(self, to_node_ptr: any | Node, strict = False) -> self:
        if isinstance(to_node_ptr, Node):
            self._db.insert_edge(from_ptr=self.ptr, to_ptr=to_node_ptr.ptr, throw_on_duplicate=strict)
        elif isinstance(to_node_ptr, dict):
            self._db.insert_edge(from_ptr=self.ptr, to_ptr=self._db.insert_node(to_node_ptr), throw_on_duplicate=strict)
        else:
            self._db.insert_edge(from_ptr=self.ptr, to_ptr=to_node_ptr, throw_on_duplicate=strict)

        return self

    def children(self) -> list[Node]:
        return [Node(connection.get(Edges.To.value), self._db) for connection in self._db.select_edge_to_ptr(self.ptr)]

    def parents(self) -> list[Node]:
        return [Node(connection.get(Edges.From.value), self._db) for connection in self._db.select_edge_from_ptr(self.ptr)]
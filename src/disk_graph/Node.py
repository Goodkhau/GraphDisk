from dataclasses import dataclass

from src.disk_graph.db.database_interface import database_interface, Edges

@dataclass(order=True)
class Node:
    def __init__(self, node_ptr, db):
        self.node_ptr = node_ptr
        self.db: database_interface = db
    
    def value(self, use_dict_fact = True):
        return self.db.select_node(self.node_ptr, use_dict_fact);

    def add(self, to_node_ptr: any | Node, strict = False) -> self:
        if isinstance(to_node_ptr, Node):
            self.db.insert_edge(from_ptr=self.node_ptr, to_ptr=to_node_ptr.node_ptr, throw_on_duplicate=strict)
        elif isinstance(to_node_ptr, dict):
            self.db.insert_edge(from_ptr=self.node_ptr, to_ptr=self.db.insert_node(to_node_ptr), throw_on_duplicate=strict)
        else:
            self.db.insert_edge(from_ptr=self.node_ptr, to_ptr=to_node_ptr, throw_on_duplicate=strict)

        return self

    def children(self) -> list[Node]:
        return [Node(connection.get(Edges.To.value), self.db) for connection in self.db.select_edge_to_ptr_from(self.node_ptr)]

    def parents(self) -> list[Node]:
        return [Node(connection.get(Edges.From.value), self.db) for connection in self.db.select_edge_from_ptr_to(self.node_ptr)]
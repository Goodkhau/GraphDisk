from src.disk_graph.db.pysqlite3.interface import NodePtrColumns

class Node:
    def __init__(self, node_ptr, db):
        self.node_ptr = node_ptr
        self.db = db
    
    def value(self, use_dict_fact = True):
        return self.db.getNode(self.node_ptr, use_dict_fact);

    def add(self, to_node_ptr: any | Node, strict = False) -> self:
        if (isinstance(to_node_ptr, Node)):
            to_node_ptr = to_node_ptr.node_ptr
        
        self.db.addConnection(from_ptr=self.node_ptr, to_ptr=to_node_ptr, throw_on_duplicate=strict)
        return self

    def children(self) -> list[Node]:
        return [Node(connection.get(EdgesColumns.To.value)) for connection in self.db.getAllChildren(self.node_ptr)]

    def parents():
        return [Node(connection.get(EdgesColumns.From.value)) for connection in self.db.getAllParents(self.node_ptr)]
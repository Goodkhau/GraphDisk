import uuid

from src.disk_graph.Node import Node

class Collection:
    def __init__(self, db: database_interface, session_id = str(uuid.uuid4())):
        self.session_id = session_id
        self.db = db
        self.db.insert_session(self.session_id)
    
    def has(self, node: Node):
        return self.db.select_collection(node_ptr=node.node_ptr, session_id=self.session_id) is not None
    
    def add(self, node: Node):
        if not self.has(node):
            _ = self.db.insert_collection(node_ptr=node.node_ptr, session_id=self.session_id)

        return self
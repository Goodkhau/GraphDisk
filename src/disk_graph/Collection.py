from typing import Self
import uuid

from src.disk_graph.db.database_interface import database_interface
from src.disk_graph.Node import Node

class Collection:
    def __init__(self, db: database_interface, session_id: str | None = None):
        self.session_id: str = session_id if session_id is not None else str(uuid.uuid4()) 
        self.db: database_interface = db
        _ = self.db.insert_session(self.session_id)
    
    def has(self, node: Node) -> bool:
        return self.db.select_collection(node_ptr=node.ptr, session_id=self.session_id) is not None
    
    def add(self, node: Node) -> Self:
        if not self.has(node):
            _ = self.db.insert_collection(node_ptr=node.ptr, session_id=self.session_id)
        return self
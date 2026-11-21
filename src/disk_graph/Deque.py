import uuid

from src.disk_graph.db.database_interface import database_interface
from src.disk_graph.Node import Node

class Deque:
    def __init__(self, db: database_interface, session_id: str | None = None):
        self.session_id: str = session_id if session_id is not None else str(uuid.uuid4())
        self.db: database_interface = db
        _ = self.db.insert_session(self.session_id)
    
    def empty(self):
        count_rows = self.db.count_deque(self.session_id)
        return count_rows == 0

    def push_front(self, node_ptr: int):
        pass

    def push_back(self, node: Node):
        back_row = self.db.select_deque_lowest(self.session_id)
        if back_row is None:
            self.db.insert_deque(position=0, node_ptr=node.ptr, session_id=self.session_id)
        else:
            self.db.insert_deque(position=back_row[1]-1, node_ptr=node.ptr, session_id=self.session_id)
        return self

    def front(self) -> Node | None:
        front_row = self.db.select_deque_highest(self.session_id)
        return Node(node_ptr=front_row[2], db=self.db) if front_row is not None else None

    def back(self):
        back_row = self.db.select_deque_lowest(self.session_id)
        return Node(node_ptr=back_row[2], db=self.db) if back_row is not None else None

    def pop_front(self):
        front_row = self.db.select_deque_highest(self.session_id)
        if front_row is None:
            return None
        deleted_row = self.db.delete_deque(position=front_row[1], session_id=self.session_id)
        return Node(node_ptr=deleted_row[2], db=self.db) if deleted_row is not None else None

    def pop_back(self):
        back_row = self.db.select_deque_lowest(self.session_id)
        if back_row is None:
            return None
        deleted_row = self.db.delete_deque(position=back_row[1], session_id=self.session_id)
        return Node(node_ptr=deleted_row[2], db=self.db) if deleted_row is not None else None
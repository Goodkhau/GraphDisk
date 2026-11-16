from src.disk_graph.Node import Node

class Deque:
    def __init__(self, db: database_interface, session_id):
        self.session_id = session_id
        self.db = db
    
    def empty(self):
        count_rows = self.db.count_deque(self.session_id)
        return count_rows == 0

    def push_front(self, node_ptr_id):
        pass

    def push_back(self, node_ptr: Node):
        back_row = self.db.select_deque_lowest(self.session_id)
        if back_row is None:
            self.db.insert_deque(position=0, node_ptr=node_ptr.node_ptr, session_id=self.session_id)
        else:
            self.db.insert_deque(position=back_row[1], node_ptr=node_ptr.node_ptr, session_id=self.session_id)
        return self

    def front(self) -> Node | None:
        front_row = self.db.select_deque_highest(self.session_id)
        return Node(self.db, front_row[2]) if front_row is not None else None

    def back(self):
        back_row = self.db.select_deque_lowest(self.session_id)
        return Node(self.db, back_row[2]) if back_row is not None else None

    def pop_front(self):
        front_row = self.db.select_deque_highest(self.session_id)
        if front_row is None:
            return None
        deleted_row = self.db.delete_deque(position=front_row[1], session_id=self.session_id)
        return Node(self.db, deleted_row[2]) if deleted_row is not None else None

    def pop_back(self):
        pass
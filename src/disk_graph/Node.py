class Node:
    def __init__(self, node_ptr, db):
        self.node_ptr = node_ptr
        self.db = db
    
    def value(self, use_dict_fact = True):
        return self.db.getNode(self.node_ptr, use_dict_fact);

    def add():
        pass
    
    def next():
        pass

    def childrens():
        pass

    def parents():
        pass
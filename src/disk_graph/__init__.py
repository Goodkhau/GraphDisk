import sqlite3 as db
from pathlib import Path

from Node import Node


graph_dir = Path(__file__).parent.parent

class graph:
    def __init__(name, remove_columns = False):
        graph_path = Path.joinpath(graph_dir, name, "graph.db")
        initialize_db = not graph_path.exists() or not graph_path.is_file()

        graph_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db = db.connect(graph_path)

        if initialize_db:
            cur = self.db.cursor()

    def createNode():
        cur = self.db.cursor()
        pk = cur.lastrowid
        return Node(pk, self.db)

    def getNode():
        cur = self.db.cursor()
        cur.execute("""
            SELECT *
            FROM vertices

        """)
        return Node()
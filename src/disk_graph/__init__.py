import sqlite3 as db
from pathlib import Path
import json

from Node import Node

graph_dir = Path(__file__).parent.parent
default_config = {}

class graph:
    def __init__(name, remove_columns = False):
        self.folder_path = Path.joinpath(graph_dir, name)
        self.config_path = Path.joinpath(folder_path, "config.json")
        self.graph_path = Path.joinpath(folder_path, "graph.db")

        graph_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = db.connect(graph_path)
        cur = self.db.cursor()

        if not self.config_path.exists():
            self.config_path.touch()
            with open(config_path, "w") as file:
                json.dump(default_config)
        
        self.createTables()

        existing_columns = cur.execute("SELECT * FROM pragma_table_info('node');")
        with open(config_path, "r", encoding="utf-8") as file:
            existing_config = json.load(file)
        

        ## calculate missing columns
        ## Update Node table with missing columns
        ## Update config.json

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
    
    # We will create the Node table later as it depends on what the user has in config.json
    def createTables():
        self.db.executescript("""
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS node_ptr (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            );
            CREATE TABLE IF NOT EXISTS verticies (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                from INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE,
                to   INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE,
            );
        """)
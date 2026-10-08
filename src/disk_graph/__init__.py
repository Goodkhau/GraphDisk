from pathlib import Path
import json

from base.db.pysqlite3 import pysqlite3 as db
from Node import Node

graph_dir = Path(__file__).parent.parent
default_config = {}

class graph:
    def __init__(name, remove_columns = False):
        self.folder_path = Path.joinpath(graph_dir, name)
        self.config_path = Path.joinpath(folder_path, "config.json")
        self.db = db(name)

        graph_path.parent.mkdir(parents=True, exist_ok=True)

        self.updateTables()
    
    def updateTables():
        self.db.createTables()
        existing_columns = self.db.getTableColumns('node')

        if not self.config_path.exists():
            self.config_path.touch()
            with open(config_path, "w") as file:
                json.dump(default_config)
        
        with open(config_path, "r", encoding="utf-8") as file:
            existing_config = json.load(file)
        

        new_columns, new_config = self.calculateRowCreation(existing_columns, existing_config)

        ## calculate missing columns
        ## Update Node table with missing columns
        ## Update config.json
    
    def calculateRowCreation(existing_columns, existing_config):
        return (
            [column for column in existing_columns if column.name not in existing_config.keys()],
            [(col_name, col_type) for col_name, col_type in existing_config if any(col_name == column.name for column in existing_columns)]
        )
    
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
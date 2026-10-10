from pathlib import Path
import json

from src.disk_graph.db.pysqlite3 import pysqlite3 as db
from src.disk_graph.Node import Node

default_config = {}

def calculateRowCreation(existing_columns: list[dict], existing_config: dict) -> tuple(list[dict], list[dict]):
    present_columns = [{'name': column['name'], 'type': column['type']} for column in existing_columns]
    missing_columns = [{'name': config_name, 'type': config_type} for config_name, config_type in existing_config.items() if not any(
        config_name == column['name'] for column in existing_columns
    )]

    return (
        missing_columns,
        present_columns + missing_columns
    )

class graph:
    def __init__(name, graph_dir = Path(__file__).parent.parent):
        self.folder_path = Path.joinpath(graph_dir, name)
        self.config_path = Path.joinpath(folder_path, "config.json")
        self.db = db(name)

        self.updateTables()
    
    def updateTables():
        self.db.createTables()
        existing_columns = self.db.getTableColumns('node')

        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.touch()
            with open(config_path, "w") as file:
                json.dump(default_config, file)

        with open(config_path, "r", encoding="utf-8") as file:
            existing_config = json.load(file)

        new_columns, updated_config = calculateRowCreation(existing_columns, existing_config)

        success_cols, failed_cols = self.db.createNodeColumns(new_columns)
        for failed_col in failed_cols:
            updated_config.pop(failed_col, None)

        with open(config_path, "w") as file:
            json.dump(updated_config, file)
    
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
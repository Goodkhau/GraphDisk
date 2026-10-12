from pathlib import Path
import json

from src.disk_graph.db.pysqlite3.interface import valid_column_types, pysqlite3_interface as db
from src.disk_graph.Node import Node

default_config = {
    "message": """Create the columns you need here in JSON where the field will be the name and the value will be the type of the column. An "id" field is required
string -> TEXT
number -> INTEGER
    """
}

def calculateRowCreation(existing_columns: list[dict], existing_config: dict) -> tuple(list[dict], list[dict]):
    present_columns = [{'name': column['name'], 'type': column['type']} for column in existing_columns]
    missing_columns = [{'name': config_name, 'type': config_type} for config_name, config_type in existing_config.items() if not any(
        config_name == column['name'] for column in existing_columns
    )]

    return (
        missing_columns,
        { column['name']: column['type'] for column in present_columns + missing_columns }
    )

class Graph:
    def __init__(self, name, node_pk_type: valid_column_types = "INTEGER", graphs_folder = Path(__file__).parent.parent):
        self.graph_path = Path.joinpath(graphs_folder, name)
        self.config_path = Path.joinpath(self.graph_path, "config.json")

        self.graph_path.mkdir(parents=True, exist_ok=True)
        self.db = db(name, graphs_folder=graphs_folder)

        self.db.createTables(node_pk_type=node_pk_type)
        self.updateTables()
    
    def updateTables(self):
        existing_columns = self.db.getTableColumns('node')

        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.touch()
            with open(self.config_path, "w") as file:
                json.dump(default_config, file, indent=4)

        with open(self.config_path, "r", encoding="utf-8") as file:
            existing_config = json.load(file)
        existing_config.pop("message", None)

        new_columns, updated_config = calculateRowCreation(existing_columns, existing_config)

        success_cols, failed_cols = self.db.createNodeColumns(new_columns)
        for failed_col in failed_cols:
            updated_config.pop(failed_col, None)

        with open(self.config_path, "w") as file:
            json.dump(updated_config, file)
    
    def createNode(self, row_data: dict):
        pk = self.db.insertNode(row_data)
        return Node(pk, self.db)

    def getNode():
        cur = self.db.cursor()
        cur.execute("""
            SELECT *
            FROM vertices

        """)
        return Node()
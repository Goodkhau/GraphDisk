import json
import logging
from pathlib import Path

from src.disk_graph.db.pysqlite3.interface import ColumnType, Sqlite3Interface as db
from src.disk_graph.db.database_interface import database_interface
from src.disk_graph.Node import Node

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_config = {
    "message": """Create the columns you need here in JSON where the field will be the name and the value will be the type of the column. An "id" field is required
string -> TEXT
number -> INTEGER
    """
}

def calculateRowCreation(existing_columns: list[dict], existing_config: dict) -> tuple(list[dict], list[dict]):
    for column in existing_columns:
        column['type'] = ColumnType(column['type']).name

    present_columns = [{'name': column['name'], 'type': column['type']} for column in existing_columns]
    missing_columns = [{'name': config_name, 'type': config_type} for config_name, config_type in existing_config.items() if not any(
        config_name == column['name'] for column in existing_columns
    )]

    return (
        missing_columns,
        { column['name']: column['type'] for column in present_columns + missing_columns }
    )

class Graph:
    def __init__(self, name: str, node_pk_type = ColumnType.Integer, graphs_folder: Path = Path.cwd() / "graphs"):
        self.graph_path = Path.joinpath(graphs_folder, name)
        self.config_path = Path.joinpath(self.graph_path, "config.json")

        self.graph_path.mkdir(parents=True, exist_ok=True)
        try:
            self.db: database_interface = db(name, graphs_folder=graphs_folder, node_pk_type=node_pk_type)
        except Exception as Error:
            logger.critical("Failed to create required tables")
            raise Exception("Failed essential graph creation dependency") from Error
        else:
            self.updateTables()
    
    def updateTables(self):
        existing_columns = self.db.getTableColumns('node')
        existing_config = self.readConfigFile()

        new_columns, updated_config = calculateRowCreation(existing_columns, existing_config)

        success_cols, failed_cols = self.db.createNodeColumns(new_columns)
        for failed_col in failed_cols:
            updated_config.pop(failed_col, None)

        self.updateConfigFile(updated_config)

    def ifConfigNotExists(self):
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.touch()
            self.updateConfigFile({})
    
    def updateConfigFile(self, new_config: dict[str, str], update_tables = False):
        try:
            self.ifConfigNotExists()

            with open(self.config_path, "w") as file:
                json.dump(default_config | new_config, file, indent=4)

            if update_tables:
                self.updateTables()
            return self
        except json.JSONDecodeError as Error:
            logger.error("Invalid JSON")
            raise Exception("Invalid JSON")
        except Exception as Error:
            logger.Error()
            raise Exception("Unexpected Error")

    def readConfigFile(self, include_message = False) -> dict[str, ColumnType]:
        try:
            self.ifConfigNotExists()

            with open(self.config_path, "r", encoding="utf-8") as file:
                config = json.load(file)
                if not include_message:
                    config.pop("message", None)
                return config
        except json.JSONDecodeError as Error:
            logger.Error()
            raise Exception("Invalid JSON")
        except Exception as Error:
            logger.Error()
            raise Exception("Unexpected Error")
    
    def createNode(self, row_data: dict = {}) -> Node:
        node_ptr_id = self.db.insertNode(row_data)
        return Node(node_ptr_id, self.db)

    def getNode(self, pk) -> Node:
        row = self.db.getNode(pk)
        return None if row == None else Node(row.get("id"), self.db)
    
    def getAllNodeValuesByPage(self, page_size = 1000, use_dict_fact = True) -> Generator[list[dict | tuple]]:
        return self.db.paginateAllNodes(page_size, use_dict_fact)
    
    def bfsGenerator(self, node: Node):
        session_id = str(uuid.uuid4())
        deque = self.db.Deque(session_id)
        visited = self.db.Visited(session_id)

        deque.push_back(node.node_ptr)
        while not deque.empty():
            front = deque.pop_front()

            if visted.has(front):
                continue
            visited.add(front)

            children = self.getAllChildren(front)
            for child in children:
                if visited.has(child):
                    continue
                deque.push_back(child)
            
            yield front
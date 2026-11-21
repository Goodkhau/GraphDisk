import json
import logging
from typing import Self
from collections.abc import Generator
import uuid
from pathlib import Path

from src.disk_graph.db.pysqlite3 import ColumnType as ColumnType, Sqlite3Interface as db
from src.disk_graph.db.database_interface import database_interface
from src.disk_graph.Node import Node
from src.disk_graph.Deque import Deque
from src.disk_graph.Collection import Collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_config = {
    "message": """Create the columns you need here in JSON where the field will be the name and the value will be the type of the column. An "id" field is required
string -> TEXT
number -> INTEGER
    """
}

def calculateColumnCreation(existing_columns: list[dict[str, str]], existing_config: dict[str, str]):
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
    def __init__(self, name: str, node_pk_type: ColumnType = ColumnType.Integer, graphs_folder: Path = Path.cwd() / "graphs"):  # pyright: ignore[reportCallInDefaultInitializer]
        self.graph_path: Path = Path.joinpath(graphs_folder, name)
        self.config_path: Path = Path.joinpath(self.graph_path, "config.json")

        self.graph_path.mkdir(parents=True, exist_ok=True)
        try:
            self.db: database_interface = db(name, graphs_folder=graphs_folder, node_pk_type=node_pk_type)
        except Exception as Error:
            logger.critical("Failed to create required tables")
            raise Exception(f"Failed essential graph creation dependency. Error: {Error}")
        else:
            _ = self.updateTables()
    
    def updateTables(self) -> Self:
        existing_columns = self.db.select_table_columns('node')
        existing_config = self.readConfigFile()

        new_columns, updated_config = calculateColumnCreation(existing_columns, existing_config)

        _, failed_cols = self.db.alter_node_columns(new_columns)
        for failed_col in failed_cols:
            _ = updated_config.pop(failed_col, None)

        return self.updateConfigFile(updated_config)

    def ifConfigNotExists(self):
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.touch()
            _ = self.updateConfigFile({})
    
    def updateConfigFile(self, new_config: dict[str, str], update_tables: bool = False):
        try:
            self.ifConfigNotExists()

            with open(file=self.config_path, mode="w") as file:
                json.dump(default_config | new_config, file, indent=4)

            return self.updateTables() if update_tables else self
        except json.JSONDecodeError as Error:
            logger.error("Invalid JSON")
            raise Exception("Invalid JSON:", Error)
        except Exception as Error:
            logger.error("Unexpected Error")
            raise Exception("Unexpected Error:", Error)

    def readConfigFile(self, include_message: bool = False) -> dict[str, str]:
        try:
            self.ifConfigNotExists()

            with open(file=self.config_path, mode="r", encoding="utf-8") as file:
                config: dict[str, str] = json.load(file)  # pyright: ignore[reportAny]
                if not include_message:
                    _ = config.pop("message", None)
                return config
        except json.JSONDecodeError as Error:
            logger.error("Invalid JSON")
            raise Exception("Invalid JSON:", Error)
        except Exception as Error:
            logger.error("Unexpected Error")
            raise Exception("Unexpected Error")
    
    def createNode(self, row_data: dict[str, str | int]) -> Node:
        node_ptr_id = self.db.insert_node(row_data)
        return Node(node_ptr=node_ptr_id, db=self.db)

    def getNode(self, pk: int) -> Node | None:
        row = self.db.select_node(pk, False)
        return None if row == None else Node(node_ptr=row[0], db=self.db)
    
    def getAllNodeValuesByPage(self, page_size: int = 1000, use_dict_fact: bool = True) -> Generator[list[dict[str, str | int]] | tuple[tuple[str | int]], None, None]:
        return self.db.paginate_all_node_ptr(page_size, use_dict_fact)
    
    def createDeque(self, session_id: str | None = None) -> Deque:
        return Deque(db=self.db, session_id=session_id if session_id is not None else str(uuid.uuid4()))
    
    def createCollection(self, session_id: str | None = None) -> Collection:
        return Collection(db=self.db, session_id=session_id if session_id is not None else str(uuid.uuid4()))
    
    def bfsGenerator(self, root: Node):
        session_id = str(uuid.uuid4())
        deque = self.createDeque(session_id)
        visited = self.createCollection(session_id)

        _ = deque.push_back(root)
        while not deque.empty():
            front = deque.pop_front()
            assert front is not None

            if visited.has(front):
                continue
            _ = visited.add(front)

            children = front.children()
            for child in children:
                if visited.has(child):
                    continue
                _ = deque.push_back(child)
            
            yield front
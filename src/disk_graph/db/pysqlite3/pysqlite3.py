import sqlite3 as db
from pathlib import Path

from src.disk_graph.db.database_interface import database_interface

graph_dir = Path(__file__).parent.parent.parent.parent

def dict_factory(cursor, row):
    return {col[0]: val for col, val in zip(cursor.description, row)}

class pysqlite3(database_interface):
    def __init__(name):
        self.folder_path = Path.joinpath(graph_dir, name)
        self.graph_path = Path.joinpath(folder_path, "graph.db")
        self.db = db.connect(graph_path)

    # We will create the Node table later as it is dependent on what the user has in config.json
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
    
    def getTableColumns():
        self.db.row_factory = dict_factory
        return self.db.execute("SELECT * FROM pragma_table_info('node');").fetchone()

    def createNodeColumns(self, new_columns: list[dict]):
        if not len(self.getTableColumns()):
            primary_key = [column for column in new_columns if column['name'] == 'id']
            if not len(primary_key) == 1:
                raise Exception(
                    f"Expecting unique indentifier 'id' column in config.json"
                )
            
            self.db.execute(f"""
                CREATE TABLE IF NOT EXISTS node (
                    id {primary_key[0]['type']} PRIMARY KEY
                );
                ALTER TABLE node_ptr
                ADD COLUMN id {primary_key[0]['type']}
                REFERENCES node(id);
            """)

        successful_creation = []
        failed_creation = []
        for column in new_columns:
            try:
                self.db.execute(f"""
                    ALTER TABLE node
                    ADD COLUMN {column['name']} {column['type']}
                """)
                successful_creation.append(column['name'])
            except:
                failed_creation.append(column['name'])

        return (
            successful_creation,
            failed_creation
        )
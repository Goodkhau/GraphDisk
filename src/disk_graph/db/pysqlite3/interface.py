import sqlite3 as db
from pathlib import Path
from typing import Literal

from src.disk_graph.db.database_interface import database_interface

valid_column_types = Literal["INTEGER", "REAL", "TEXT", "BLOB"]

def dict_factory(cursor, row):
    return {col[0]: val for col, val in zip(cursor.description, row)}

class pysqlite3_interface(database_interface):
    def __init__(self, name, graphs_folder):
        self.graph_path = Path.joinpath(graphs_folder, name)
        self.database_file = Path.joinpath(self.graph_path, "graph.db")

        self.db = db.connect(self.database_file)

    def createTables(self, node_pk_type = "INTEGER"):
        self.db.executescript(f"""
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS node (
                id {node_pk_type} PRIMARY KEY
            ) STRICT;
            CREATE TABLE IF NOT EXISTS node_ptr (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                node    {node_pk_type} NOT NULL REFERENCES node(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS verticies (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                from_node   INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE,
                to_node     INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE
            );
        """)
    
    def getTableColumns(self, name):
        self.db.row_factory = dict_factory
        return self.db.execute(f"SELECT * FROM pragma_table_info('{name}');").fetchall()
        #return column_info if column_info != None else []

    def createNodeColumns(self, new_columns: list[dict]):
        successful_creation = []
        failed_creation = []
        for column in new_columns:
            if column['name'] == 'id':
                continue

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
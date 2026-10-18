import sqlite3 as db
from pathlib import Path
from typing import Literal
from enum import Enum

from src.disk_graph.db.database_interface import database_interface

valid_column_types = Literal["Integer", "Float", "String", "Blob"]

def dict_factory(cursor, row):
    return {col[0]: val for col, val in zip(cursor.description, row)}

def calculateRowInsertion(columns: list[dict], row_data: dict) -> tuple(str, list):
    insert_data = [row_data.get(column['name']) for column in columns]

    return (
        "(" + ",".join("?" * len(columns)) + ")",
        insert_data
    )

class ColumnType(str, Enum):
    Integer   = "INTEGER"
    Float     = "REAL"
    String    = "TEXT"
    Bytes     = "BLOB"

    # This function overrides enum indexing failure. Makes indexing this enum soft casing.
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return super()._missing_(value)

class Sqlite3Interface(database_interface):
    def __init__(self, name, graphs_folder):
        self.graph_path = Path.joinpath(graphs_folder, name)
        self.database_file = Path.joinpath(self.graph_path, "graph.db")

        self.db = db.connect(self.database_file)

    def createTables(self, node_pk_type = ColumnType.Integer.name):
        self.db.executescript(f"""
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS node (
                id {ColumnType[node_pk_type].value} PRIMARY KEY
            ) STRICT;
            CREATE TABLE IF NOT EXISTS node_ptr (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                node    {ColumnType[node_pk_type].value} NOT NULL REFERENCES node(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS verticies (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                from_node   INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE,
                to_node     INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE
            );
        """)
    
    def getTableColumns(self, name):
        self.db.row_factory = dict_factory
        try:
            return self.db.execute(f"SELECT * FROM pragma_table_info('{name}');").fetchall()
        except Exception as Error:
            print(f"pysqlite3/interface.py: Failed to get column info for {name}.", Error)
            return []

    def createNodeColumns(self, new_columns: list[dict]):
        successful_creation = []
        failed_creation = []
        for column in new_columns:
            if column['name'] == 'id':
                continue

            try:
                self.db.execute(f"""
                    ALTER TABLE node
                    ADD COLUMN {column['name']} {ColumnType[column['type']].value};
                """)
            except (ValueError, KeyError) as Error:
                print(
                    f"pysqlite3/interface.py: Failed to create column {column['name']} because of invalid column type:" + 
                    f"{column['type']}. Expecting one of {[enum.name for enum in ColumnType]}.",
                    Error
                )
                failed_creation.append(column['name'])
            except Exception as Error:
                print(f"pysqlite3/interface.py: Failed to create column {column['name']} with type {column['type']}:", Error)
                failed_creation.append(column['name'])
            else:
                successful_creation.append(column['name'])

        return (
            successful_creation,
            failed_creation
        )

    def insertNode(self, row_data: dict):
        columns = self.getTableColumns('node')

        pk = row_data.get('id')
        is_incrementing_pk = any(column['name'] == 'id' and column['type'] == 'INTEGER' for column in columns)
        if pk == None and not is_incrementing_pk:
            raise Exception(
                f"id needs to be defined for non-incrementing row."
            )

        placeholder, insert_data = self.calculateRowInsertion(columns, row_data)

        cursor = self.db.cursor()
        try:
            cursor.execute(f"""
                INSERT INTO node 
                VALUES {placeholder}
            """, insert_data)
        except:
            return None
        else:
            self.db.commit()

        return row_data.get('id') if pk != None else cursor.lastrowid
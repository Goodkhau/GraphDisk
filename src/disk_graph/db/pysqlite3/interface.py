import sqlite3
import logging
from pathlib import Path
from typing import Literal
from enum import Enum
from contextlib import closing

from src.disk_graph.db.database_interface import database_interface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    def __init__(self, name: str, graphs_folder: str):
        self.graph_path = Path.joinpath(graphs_folder, name)
        self.database_file = Path.joinpath(self.graph_path, "graph.db")

    def createTables(self, node_pk_type: str = ColumnType.Integer.name):
        try:
            conn = sqlite3.connect(self.database_file)
            conn.executescript(f"""
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS node (
                    id      {ColumnType[node_pk_type].value} PRIMARY KEY
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
        finally:
            conn.close()

    def getTableColumns(self, name: str):
        try:
            conn = sqlite3.connect(self.database_file)
            conn.row_factory = dict_factory
            return conn.execute(f"SELECT * FROM pragma_table_info('{name}');").fetchall()
        except Exception:
            logger.exception(f"Failed to get column info for {name}.")
            return []
        finally:
            conn.close()

    def createNodeColumns(self, new_columns: list[dict]):
        successful_creation = []
        failed_creation = []
        for column in new_columns:
            if column['name'] == 'id':
                continue

            try:
                conn = sqlite3.connect(self.database_file)
                conn.execute(f"""
                    ALTER TABLE node
                    ADD COLUMN {column['name']} {ColumnType[column['type']].value};
                """)
            except (ValueError, KeyError):
                logger.exception(
                    f"Failed to create column {column['name']} because of invalid column type:" + 
                    f"{column['type']}. Expecting one of {[enum.name for enum in ColumnType]}."
                )
                failed_creation.append(column['name'])
            except Exception:
                logger.exception(f"Failed to create column {column['name']} with type {column['type']}:")
                failed_creation.append(column['name'])
            else:
                successful_creation.append(column['name'])
            finally:
                conn.close()

        return (
            successful_creation,
            failed_creation
        )

    def insertNode(self, row_data: dict):
        columns = self.getTableColumns('node')

        pk = row_data.get('id')
        is_incrementing_pk = any(column['name'] == 'id' and column['type'] == ColumnType.Integer.value for column in columns)
        if pk == None and not is_incrementing_pk:
            raise Exception(
                f"id needs to be defined for non-incrementing row."
            )

        placeholder, insert_data = self.calculateRowInsertion(columns, row_data)

        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute(
                f"""
                    INSERT INTO node 
                    VALUES {placeholder}
                """,
                insert_data
            )
        except Exception:
            conn.rollback()
            logger.exception("Failed to insert node.")
            return None
        else:
            conn.commit()
            return pk if pk != None else cursor.lastrowid
        finally:
            conn.close()
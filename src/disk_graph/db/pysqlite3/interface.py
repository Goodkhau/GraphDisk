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
                    id  {ColumnType[node_pk_type].value} PRIMARY KEY
                        REFERENCES node(id) ON DELETE CASCADE,
                    in_degree           INTEGER NOT NULL DEFAULT 0,
                    out_degree          INTEGER NOT NULL DEFAULT 0,
                    looped              INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS edges (
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
    
    def getNode(self, pk):
        try:
            conn = sqlite3.connect(self.database_file)
            return conn.execute(
                f"""
                    SELECT *
                    FROM node_ptr
                    WHERE id = ?
                """,
                [pk]
            ).fetchone()
        finally:
            conn.close()

    def insertNode(self, row_data: dict):
        columns = self.getTableColumns('node')

        pk = row_data.get('id')
        is_incrementing_pk = any(column['name'] == 'id' and column['type'] == ColumnType.Integer.value for column in columns)
        if pk == None and not is_incrementing_pk:
            raise Exception(
                f"id needs to be defined for non-incrementing row."
            )

        placeholder, insert_data = calculateRowInsertion(columns, row_data)

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
            cursor.execute(
                f"""
                    INSERT INTO node_ptr (id)
                    VALUES (?)
                """,
                [pk]
            )
        except sqlite3.Error as Error:
            conn.rollback()
            raise sqlite3.Error(f"Sqlite3Interface: Failed to insert column {row_data} into table 'node' {Error}")
        except Exception as Error:
            conn.rollback()
            raise Exception(f"Sqlite3Interface: Unexpected error {Error}")
        else:
            conn.commit()
            pk = pk if pk != None else cursor.lastrowid

            match next(column["type"] for column in columns):
                case ColumnType.Integer.value:
                    pk = int(pk)
                case ColumnType.String.value:
                    pk = str(pk)
            
            return pk
        finally:
            conn.close()
    
    def paginateAllNodes(self, page_size, use_dict_fact):
        MAX_PAGE_SIZE = 10000
        MIN_PAGE_SIZE = 100
        page_size = min(MAX_PAGE_SIZE, page_size)
        page_size = max(MIN_PAGE_SIZE, page_size)

        rows = True
        last = False
        while True:
            try:
                conn = sqlite3.connect(self.database_file)
                if use_dict_fact:
                    conn.row_factory = dict_factory

                rows = conn.execute(
                    "SELECT * FROM node WHERE id > ? ORDER BY id LIMIT ?" if last else "select * FROM node ORDER BY id LIMIT ?",
                    (last, page_size) if last else (page_size,)
                ).fetchall()
            except:
                logger.exception(f"Failed to get row for page size {page_size} and last {last}")
                return []
            else:
                if not rows:
                    return []

                yield rows
                last = rows[-1].get('id') if use_dict_fact else rows[-1][0]
            finally:
                conn.close()
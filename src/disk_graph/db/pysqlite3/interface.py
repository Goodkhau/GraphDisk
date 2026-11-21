import sqlite3
from pathlib import Path
from typing import Literal, overload, override, cast
from collections.abc import Generator
from enum import Enum
from contextlib import closing
 
from src.disk_graph.db.database_interface import database_interface, Edges, NodePtr
 
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
 
class Collection(str, Enum):
    NodePtr = "node_ptr_id"
    Session = "session_id"
 
class Deque(str, Enum):
    Position    = "position"
    NodePtr     = "node_ptr"
    Session     = "session_id"
 
class Sqlite3Interface(database_interface):
    def __init__(self, name: str, graphs_folder: Path, node_pk_type: ColumnType):
        self.graph_path: Path = Path.joinpath(graphs_folder, name)
        self.graph_path.mkdir(parents=True, exist_ok=True)
 
        self.database_file = Path.joinpath(self.graph_path, "graph.db")
        self.create_tables(node_pk_type=node_pk_type)
 
    def insert_session(self, session_id: str) -> str:
        with closing(sqlite3.connect(self.database_file)) as conn, conn as transaction:
            cursor = transaction.cursor()
            cursor.execute(
                f"""
                    INSERT OR IGNORE INTO session
                    VALUES (?)
                """,
                (session_id,)
            )

        return session_id
 
    def create_tables(self, node_pk_type: ColumnType):
        with closing(sqlite3.connect(self.database_file)) as conn:
            _ = conn.executescript(f"""
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS node (
                    id {ColumnType[node_pk_type.name].value} PRIMARY KEY
                ) STRICT;
 
                CREATE TABLE IF NOT EXISTS node_ptr (
                    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
                    {NodePtr.Node.value}        INTEGER NOT NULL REFERENCES node(id),
                    {NodePtr.InDegree.value}    INTEGER NOT NULL DEFAULT 0,
                    {NodePtr.OutDegree.value}   INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_node_ptr_node ON node_ptr(node);
 
                CREATE TABLE IF NOT EXISTS edges (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    {Edges.From.value}  INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE,
                    {Edges.To.value}    INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_edges_from_node ON edges({Edges.From.value});
                CREATE INDEX IF NOT EXISTS idx_edges_to_node ON edges({Edges.To.value});
 
                CREATE TABLE IF NOT EXISTS session (
                    id TEXT PRIMARY KEY
                );
 
                CREATE TABLE IF NOT EXISTS collection (
                    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
                    {Collection.NodePtr.value}  INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE,
                    {Collection.Session.value}  TEXT NOT NULL REFERENCES session(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_collection_nodeptrid_session ON collection({Collection.NodePtr.value},{Collection.Session.value});
 
                CREATE TABLE IF NOT EXISTS deque (
                    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                    {Deque.Position.value}  INTEGER NOT NULL,
                    {Deque.NodePtr.value}   INTEGER NOT NULL REFERENCES node_ptr(id) ON DELETE CASCADE,
                    {Deque.Session.value}   TEXT NOT NULL REFERENCES session(id) ON DELETE CASCADE
                );
            """)
 
    @override
    def select_tables(self) -> list[str]:
        with closing(sqlite3.connect(self.database_file)) as conn:
            tables = conn.execute(
                """
                    SELECT name
                    FROM sqlite_schema
                    WHERE type='table'
                        AND name NOT LIKE 'sqlite.%';
                """
            ).fetchall()
 
            return [table[0] for table in tables]
 
    @override
    def select_table_columns(self, name: str) -> list[dict[str, str]]:
        with closing(sqlite3.connect(self.database_file)) as conn:
            conn.row_factory = dict_factory
            return conn.execute(f"SELECT * FROM pragma_table_info('{name}');").fetchall()
 
    @override
    def alter_node_columns(self, new_columns: list[dict[str,str | ColumnType]]):
        successful_creation: list[str] = []
        failed_creation: list[str] = []
        with closing(sqlite3.connect(self.database_file)) as conn:
            for column in new_columns:
                if column['name'] == 'id':
                    continue

                try:
                    _ = conn.execute(f"""
                        ALTER TABLE node
                        ADD COLUMN {column['name']} {ColumnType[column['type']].value};
                    """)
                except:
                    failed_creation.append(column['name'])
                else:
                    successful_creation.append(column['name'])
 
        return (
            successful_creation,
            failed_creation
        )

    @overload
    def select_node(self, node_ptr: int, use_dict_fact: Literal[True]) -> dict[str, str | int] | None: ...

    @overload
    def select_node(self, node_ptr: int, use_dict_fact: Literal[False]) -> tuple[list[str | int]] | None: ...

    @override
    def select_node(self, node_ptr: int, use_dict_fact: bool) -> dict[str, str | int] | tuple[list[str | int]] | None:
        with closing(sqlite3.connect(self.database_file)) as conn:
            if use_dict_fact:
                conn.row_factory = dict_factory
            return conn.execute(
                f"""
                    SELECT node.*
                    FROM node_ptr AS ptr
                    LEFT JOIN node AS node
                        ON ptr.{NodePtr.Node.value} = node.id
                    WHERE ptr.id = ?
                """,
                (node_ptr,)
            ).fetchone()
 
    def insert_node(self, row_data: dict[str, str | int]):
        columns = self.select_table_columns('node')
 
        pk = row_data.get('id')
        is_incrementing_pk = any(column['name'] == 'id' and column['type'] == ColumnType.Integer.value for column in columns)
        if pk == None and not is_incrementing_pk:
            raise Exception(
                f"id needs to be defined for non-incrementing row."
            )
 
        placeholder, insert_data = calculateRowInsertion(columns, row_data)
 
        with closing(sqlite3.connect(self.database_file)) as conn, conn as transaction:
            cursor = transaction.cursor()
 
            existing_node_ptr = cursor.execute(
                f"""
                    SELECT ptr.id
                    FROM node_ptr AS ptr
                    INNER JOIN node AS node
                        ON ptr.{NodePtr.Node.name} = node.id
                    WHERE node.id = (?)
                """,
                (pk,)
            ).fetchone()
 
            if existing_node_ptr:
                return existing_node_ptr[0]
 
            cursor.execute(
                f"""
                    INSERT INTO node 
                    VALUES {placeholder}
                """,
                insert_data
            )
 
            pk = pk if pk != None else cursor.lastrowid
            cursor.execute(
                f"""
                    INSERT INTO node_ptr ({NodePtr.Node.value})
                    VALUES (?)
                """,
                (pk,)
            )
        return cursor.lastrowid
    
    def insert_edge(self, from_ptr, to_ptr, throw_on_duplicate):
        with closing(sqlite3.connect(self.database_file)) as conn, conn as transaction:
            cursor = transaction.cursor()
 
            existing_connection = cursor.execute(
                f"""
                    SELECT id
                    FROM edges
                    WHERE {Edges.From.value} = (?)
                        AND {Edges.To.value} = (?)
                """,
                (from_ptr, to_ptr,)
            ).fetchone()
 
            if existing_connection:
                return
 
            cursor.execute(
                f"""
                    INSERT INTO edges
                        ({Edges.From.value},{Edges.To.value})
                    VALUES (?,?)
                """,
                (from_ptr, to_ptr,)
            )
        return cursor.lastrowid
    
    def select_edge_to_ptr(self, from_node_ptr, use_dict_fact = True) -> list[ dict[EdgesColumns.To.value, int] | tuple(any) ]:
        with closing(sqlite3.connect(self.database_file)) as conn:
            if use_dict_fact:
                conn.row_factory = dict_factory
            return conn.execute(
                f"""
                    SELECT {Edges.To.value}
                    FROM edges
                    WHERE {Edges.From.value} = (?)
                """,
                (from_node_ptr,)
            ).fetchall()
    
    def select_edge_from_ptr(self, to_node_ptr, use_dict_fact = True):
        with closing(sqlite3.connect(self.database_file)) as conn:
            if use_dict_fact:
                conn.row_factory = dict_factory
            return conn.execute(
                f"""
                    SELECT {Edges.From.value}
                    FROM edges
                    WHERE {Edges.To.value} = (?)
                """,
                (to_node_ptr,)
            ).fetchall()

    @override
    def paginate_all_node_ptr(self, page_size: int, use_dict_fact: bool) -> Generator[list[dict[str, str | int]] | tuple[tuple[str | int]]]:
        MAX_PAGE_SIZE = 10000
        MIN_PAGE_SIZE = 100
        page_size = min(MAX_PAGE_SIZE, page_size)
        page_size = max(MIN_PAGE_SIZE, page_size)
 
        last = False
        while True:
            with closing(sqlite3.connect(self.database_file)) as conn:
                if use_dict_fact:
                    conn.row_factory = dict_factory
 
                rows = conn.execute(
                    "SELECT * FROM node WHERE id > ? ORDER BY id LIMIT ?" if last else "select * FROM node ORDER BY id LIMIT ?",
                    (last, page_size,) if last else (page_size,)
                ).fetchall()
 
                if not rows:
                    return
 
                yield rows
                last = rows[-1].get('id') if use_dict_fact else rows[-1][0]
    
    def insert_deque(self, position: int, node_ptr: int, session_id: str):
        with sqlite3.connect(self.database_file) as conn:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute(
                f"""
                    INSERT INTO deque
                        ({Deque.Position.value},{Deque.NodePtr.value},{Deque.Session.value})
                    VALUES (?,?,?)
                """,
                (position, node_ptr, session_id,)
            )
            conn.commit()
            return node_ptr
    
    @override
    def select_deque_highest(self, session_id: str) -> tuple[int, int, int, str] | None:
        with closing(sqlite3.connect(self.database_file)) as conn:
            highest: tuple[int, int, int, str] = conn.execute(
                f"""
                    SELECT *
                    FROM deque
                    WHERE {Deque.Session.value} = ?
                    ORDER BY {Deque.Position.value} DESC
                    LIMIT 1
                """,
                (session_id,)
            ).fetchone()
        
        return highest
    
    @override
    def select_deque_lowest(self, session_id: str) -> tuple[int, int, int, str] | None:
        with closing(sqlite3.connect(self.database_file)) as conn:
            lowest: tuple[int, int, int, str] = conn.execute(
                f"""
                    SELECT *
                    FROM deque
                    WHERE {Deque.Session.value} = ?
                    ORDER BY {Deque.Position.value} ASC
                    LIMIT 1
                """,
                (session_id,)
            ).fetchone()
        
        return lowest
    
    @override
    def delete_deque(self, position: int, session_id: str) -> tuple[int, int, int, str] | None:
        with closing(sqlite3.connect(self.database_file)) as conn, conn as transaction:
            cursor = transaction.cursor()
            deleted_rows: list[tuple[int, int, int, str]] = cursor.execute(
                f"""
                    DELETE FROM deque
                    WHERE {Deque.Session.value} = ?
                        AND {Deque.Position.value} = ?
                    RETURNING *
                """,
                (session_id,position,)
            ).fetchall()

        return deleted_rows[0] if deleted_rows else None
 
    def count_deque(self, session_id: str) -> int:
        with closing(sqlite3.connect(self.database_file)) as conn:
            num_rows: int =  conn.execute(
                f"""
                    SELECT COUNT(*)
                    FROM deque
                    WHERE {Deque.Session.value} = ?
                """,
                (session_id,)
            ).fetchone()[0]
        
        return num_rows
    
    def insert_collection(self, node_ptr: int, session_id: str) -> int:
        with closing(sqlite3.connect(self.database_file)) as conn, conn as transaction:
            _ = transaction.execute(
                f"""
                    INSERT OR IGNORE INTO collection
                        ({Collection.NodePtr.value},{Collection.Session.value})
                    VALUES (?,?)
                """,
                (node_ptr, session_id,)
            )
        
        return node_ptr
    
    def select_collection(self, node_ptr: int, session_id: str) -> tuple[str | int] | None:
        with closing(sqlite3.connect(self.database_file)) as conn:
            collection_row: tuple[str | int] | None = conn.execute(
                f"""
                    SELECT *
                    FROM collection
                    WHERE {Collection.NodePtr.value} = ?
                        AND {Collection.Session.value} = ?
                """,
                (node_ptr, session_id,)
            ).fetchone()

        return collection_row
import sqlite3
import logging
import uuid
from pathlib import Path
from typing import Literal
from enum import Enum
from contextlib import closing
from datetime import datetime

from src.disk_graph.db.database_interface import database_interface, Edges, NodePtr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    def __init__(self, name: str, graphs_folder: str, node_pk_type: ColumnType):
        self.graph_path = Path.joinpath(graphs_folder, name)
        self.database_file = Path.joinpath(self.graph_path, "graph.db")
        self.createTables(node_pk_type=node_pk_type)

    def insertSession(self, session_id: str):
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute(
                f"""
                    INSERT OR IGNORE INTO session
                    VALUES (?,?)
                """,
                (session_id, datetime.now(),)
            )
        except:
            conn.rollback()
            logger.error()
            raise Exception(f"Failed to insert session id: {session_id}")
        else:
            conn.commit()
            return session_id
        finally:
            conn.close()
    
    def createDeque(self, session_id = str(uuid.uuid4())):
        self.insertSession(session_id)
        return self.Deque(self, session_id)
    
    def createCollection(self, session_id = str(uuid.uuid4())):
        self.insertSession(session_id)
        return self.Collection(self, session_id)

    class Deque:
        def __init__(self, db: database_interface, session_id):
            self.session_id = session_id
            self.db = db
        
        def empty(self):
            try:
                conn = sqlite3.connect(self.db.database_file)
                return conn.execute(
                    f"""
                        SELECT COUNT(*)
                        FROM deque
                        WHERE {Deque.Session.value} = ?
                    """,
                    (self.session_id,)
                ).fetchone()[0] == 0
            finally:
                conn.close()

        def push_front(self, node_ptr_id):
            pass

        def push_back(self, node_ptr_id):
            try:
                min_pos = self.front(field=Deque.Position.value)

                conn = sqlite3.connect(self.db.database_file)
                cursor = conn.cursor()

                if min_pos is None:
                    min_pos = 0

                cursor.execute(
                    f"""
                        INSERT INTO deque
                        VALUES (?,?,?)
                    """,
                    (min_pos-1, node_ptr_id, self.session_id,)
                )
            except Exception as Error:
                conn.rollback()
                logger.error()
                raise Exception(f"Unexpected Error, failed to enque positon: {min_pos}, nodeptr: {node_ptr_id}, session: {self.session_id}")
            else:
                conn.commit()
                return node_ptr_id
            finally:
                conn.close()

        def front(self, field = Deque.NodePtr.value) -> int | None:
            try:
                conn = sqlite3.connect(self.db.database_file)
            
                min_pos = conn.execute(
                    f"""
                        SELECT {field}
                        FROM deque
                        WHERE {Deque.Session.value} = ?
                        ORDER BY {Deque.Position.value} DESC
                        LIMIT 1
                    """,
                    (self.session_id,)
                ).fetchone()

                return None if min_pos is None else min_pos[0]
            except Exception as Error:
                conn.rollback()
                logger.error()
                raise Exception(f"Unexpected Error, failed to enque positon: {min_pos[0]}, nodeptr: {node_ptr_id}, session: {self.session_id}")
            finally:
                conn.close()

        def back(self):
            try:
                conn = sqlite3.connect(self.db.database_file)
            
                min_pos = conn.execute(
                    f"""
                        SELECT {Deque.NodePtr.value}
                        FROM deque
                        WHERE {Deque.Session.value} = ?
                        ORDER BY {Deque.Position.value} ASC
                        LIMIT 1
                    """,
                    (self.session_id,)
                ).fetchone()

                return None if min_pos is None else min_pos[0]
            except Exception as Error:
                conn.rollback()
                logger.error()
                raise Exception(f"Unexpected Error, failed to enque positon: {min_pos[0]}, nodeptr: {node_ptr_id}, session: {self.session_id}")
            finally:
                conn.close()

        def pop_front(self):
            conn = None

            try:
                min_pos = self.front(field=Deque.Position.value)

                if min_pos is None:
                    return None

                conn = sqlite3.connect(self.db.database_file)
                cursor = conn.cursor()

                deleted_rows = cursor.execute(
                    f"""
                        DELETE FROM deque
                        WHERE {Deque.Position.value} = ?
                        RETURNING *
                    """,
                    (min_pos,)
                ).fetchall()
            except Exception as Error:
                conn.rollback()
                logger.error()
                raise Exception(f"Unexpected Error, failed to delete positon: {min_pos}. Error: {Error}")
            else:
                conn.commit()
                return deleted_rows[0][1]
            finally:
                if conn:
                    conn.close()

        def pop_back(self):
            pass

    class Collection:
        def __init__(self, db: database_interface, session_id = str(uuid.uuid4())):
            self.session_id = session_id
            self.db = db
            self.db.insertSession(self.session_id)
        
        def has(self, node_ptr_id):
            try:
                conn = sqlite3(self.db.database_file)
                conn.execute(
                    f"""
                        SELECT *
                        FROM collection
                        WHERE {Collection.NodePtr.value} = ?
                            AND {Collection.Session.value} = ?
                    """,
                    (node_ptr_id, self.session_id,)
                )
            except Exception:
                logger.error()
                raise Exception(f"Unexpected error, failed to check if collection 'has' {node_ptr_id} on session {self.session_id}")
            finally:
                conn.close()
        
        def add(self, node_ptr_id):
            try:
                conn = sqlite3(self.db.database_file)
                conn.execute(
                    f"""
                        INSERT OR IGNORE INTO collection
                        ({Collection.NodePtr.value},{Collection.Session.value})
                        VALUES (?,?)
                    """,
                    (node_ptr_id, self.session_id,)
                )
            except Exception:
                logger.error()
                raise Exception(f"Unexpected error, failed to check if collection 'has' {node_ptr_id} on session {self.session_id}")
            else:
                conn.commit()
                return self
            finally:
                conn.close()

    def createTables(self, node_pk_type: ColumnType):
        try:
            conn = sqlite3.connect(self.database_file)
            conn.executescript(f"""
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
                    id          TEXT PRIMARY KEY,
                    create_date INTEGER
                );

                CREATE TABLE IF NOT EXISTS collection (
                    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                    {Collection.NodePtr.value}     INTEGER REFERENCES node_ptr(id) ON DELETE CASCADE,
                    {Collection.Session.value}     TEXT NOT NULL REFERENCES session(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_collection_nodeptrid_session ON collection({Collection.NodePtr.value},{Collection.Session.value});

                CREATE TABLE IF NOT EXISTS deque (
                    {Deque.Position.value}   INTEGER PRIMARY KEY,
                    {Deque.NodePtr.value}    INTEGER REFERENCES node_ptr(id) ON DELETE CASCADE,
                    {Deque.Session.value}    TEXT NOT NULL REFERENCES session(id) ON DELETE CASCADE
                );
            """)
        finally:
            conn.close()

    def getTables(self):
        try:
            conn = sqlite3.connect(self.database_file)
            tables = conn.execute(
                """
                    SELECT name
                    FROM sqlite_schema
                    WHERE type='table'
                        AND name NOT LIKE 'sqlite.%';
                """
            ).fetchall()

            return [table[0] for table in tables]
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
                    f"Failed to create column {column['name']} because of invalid column type: " + 
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
    
    def getNode(self, node_ptr, use_dict_fact):
        try:
            conn = sqlite3.connect(self.database_file)
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
        except sqlite3.Error as Error:
            conn.rollback()
            raise sqlite3.Error(f"Sqlite3Interface: Failed to insert column {row_data} and primary key {pk} {Error}")
        except Exception as Error:
            conn.rollback()
            raise Exception(f"Sqlite3Interface: Unexpected error {Error}")
        else:
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def addConnection(self, from_ptr, to_ptr, throw_on_duplicate):
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()

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
        except Exception as Error:
            raise Exception(f"Sqlite3Interface: Unexpected error adding connection from: {from_ptr}, to: {to_ptr} {Error}")
        else:
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def getAllChildren(self, node_ptr, use_dict_fact = True) -> list[ dict[EdgesColumns.To.value, int] | tuple(any) ]:
        try:
            conn = sqlite3.connect(self.database_file)
            if use_dict_fact:
                conn.row_factory = dict_factory
            return conn.execute(
                f"""
                    SELECT {Edges.To.value}
                    FROM edges
                    WHERE {Edges.From.value} = (?)
                """,
                (node_ptr,)
            ).fetchall()
        finally:
            conn.close()
    
    def getAllParents(self, node_ptr, use_dict_fact = True):
        try:
            conn = sqlite3.connect(self.database_file)
            if use_dict_fact:
                conn.row_factory = dict_factory
            return conn.execute(
                f"""
                    SELECT {Edges.From.value}
                    FROM edges
                    WHERE {Edges.To.value} = (?)
                """,
                (node_ptr,)
            ).fetchall()
        finally:
            conn.close()

    def paginateAllNodes(self, page_size, use_dict_fact):
        MAX_PAGE_SIZE = 10000
        MIN_PAGE_SIZE = 100
        page_size = min(MAX_PAGE_SIZE, page_size)
        page_size = max(MIN_PAGE_SIZE, page_size)

        last = False
        while True:
            try:
                conn = sqlite3.connect(self.database_file)
                if use_dict_fact:
                    conn.row_factory = dict_factory

                rows = conn.execute(
                    "SELECT * FROM node WHERE id > ? ORDER BY id LIMIT ?" if last else "select * FROM node ORDER BY id LIMIT ?",
                    (last, page_size,) if last else (page_size,)
                ).fetchall()
            except:
                logger.exception(f"Failed to get row for page size {page_size} and last {last}")
                return []
            else:
                if not rows:
                    return

                yield rows
                last = rows[-1].get('id') if use_dict_fact else rows[-1][0]
            finally:
                conn.close()
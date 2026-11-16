class Collection:
    def __init__(self, db: database_interface, session_id = str(uuid.uuid4())):
        self.session_id = session_id
        self.db = db
        self.db.insert_session(self.session_id)
    
    def has(self, node_ptr_id):
        conn = sqlite3.connect(self.db.database_file)

        try:
            coll_row = conn.execute(
                f"""
                    SELECT *
                    FROM collection
                    WHERE {Collection.NodePtr.value} = ?
                        AND {Collection.Session.value} = ?
                """,
                (node_ptr_id, self.session_id,)
            ).fetchone()

            return coll_row is not None
        except Exception:
            logger.error("Failed to check if database has ptr")
            raise Exception(f"Unexpected error, failed to check if collection has ptr: {node_ptr_id} on session {self.session_id}")
        finally:
            conn.close()
    
    def add(self, node_ptr_id):
        if self.has(node_ptr_id):
            return self

        conn = sqlite3.connect(self.db.database_file)

        try:
            conn.execute(
                f"""
                    INSERT OR IGNORE INTO collection
                    ({Collection.NodePtr.value},{Collection.Session.value})
                    VALUES (?,?)
                """,
                (node_ptr_id, self.session_id,)
            )
        except Exception as Error:
            logger.error("Failed to add node_ptr")
            raise Exception(f"Unexpected error, failed to check if collection 'has' {node_ptr_id} on session {self.session_id}. Error: {Error}")
        else:
            conn.commit()
            return self
        finally:
            conn.close()
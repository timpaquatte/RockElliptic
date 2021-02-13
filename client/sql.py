import sqlite3 as sl
from os import path

def init_sql():
    relpath_db = "./ressources/client_data.db"
    abspath = path.abspath(relpath_db)

    db_exists = path.exists(abspath)

    if not db_exists:
        conn = getSQLConn()
        with conn:
            conn.execute("""
                CREATE TABLE CLIENT (
                    id INTEGER NOT NULL PRIMARY KEY,
                    first_name TEXT,
                    name TEXT,
                    balance INTEGER,
                    pubkey BLOB
                );
                """)

def getSQLConn():
    relpath_db = "./ressources/client_data.db"
    abspath = path.abspath(relpath_db)
    conn = sl.connect(abspath)
    return conn
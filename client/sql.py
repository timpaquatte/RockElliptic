import sqlite3 as sl
from os import path

from .misc import parsePubKey

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

def insertInDatabase(id_user, first_name, name, balance, pubkey):
    conn = getSQLConn()
    req = "INSERT INTO CLIENT (id, first_name, name, balance, pubkey) values (?, ?, ?, ?, ?)"
    data = (id_user, first_name, name, balance, pubkey)
    with conn:
        conn.execute(req, data)

def getEntrySQL(id_user):
    conn = getSQLConn()
    with conn:
        c = conn.execute("SELECT pubkey, balance, first_name, name  FROM CLIENT WHERE id=?", (id_user,))
        pubkey, balance, first_name, name = c.fetchone()
    pubkey, PIN = parsePubKey(pubkey)

    return first_name, name, balance, pubkey, PIN

def updateEntry(id_user, new_balance):
    conn = getSQLConn()
    req = "UPDATE CLIENT SET balance = ? WHERE id=?"
    data = (new_balance, id_user)
    with conn:
        conn.execute(req, data)
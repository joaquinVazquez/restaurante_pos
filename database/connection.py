# database/connection.py
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "restaurante_pos.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute_query(query, params=None, fetch=True):
    # Convertir sintaxis PostgreSQL → SQLite
    query = query.replace("%s", "?")
    query = query.replace("CURRENT_DATE", "DATE('now')")
    query = query.replace("CURRENT_TIMESTAMP", "DATETIME('now')")
    query = query.replace("TRUE",  "1")
    query = query.replace("FALSE", "0")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

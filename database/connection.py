# database/connection.py
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Retorna una conexión activa a PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def execute_query(query, params=None, fetch=True):
    """
    Ejecuta una consulta SQL de forma segura.
    fetch=True  → SELECT
    fetch=False → INSERT/UPDATE/DELETE
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                else:
                    return cur.rowcount
    finally:
        conn.close()
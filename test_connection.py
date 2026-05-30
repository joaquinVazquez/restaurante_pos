# test_connection.py
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio FROM productos LIMIT 3;")
    rows = cursor.fetchall()

    print("✅ ¡Conexión exitosa!")
    print("📋 Primeros productos en la BD:")
    for row in rows:
        print(f"   → {row[0]}: ${row[1]}")

    conn.close()

except Exception as e:
    print(f"❌ Error de conexión: {e}")
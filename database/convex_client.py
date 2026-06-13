# database/convex_client.py
import requests
import os

# URL de tu deployment de Convex
CONVEX_URL = "https://next-badger-972.convex.cloud"


def convex_query(path: str, args: dict = None):
    """Ejecuta una query en Convex y retorna los datos."""
    try:
        response = requests.post(
            f"{CONVEX_URL}/api/query",
            json={
                "path": path,
                "args": args or {},
                "format": "json",
            },
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            print(f"❌ Error Convex query {path}: {data}")
            return []

        return data.get("value", [])

    except requests.exceptions.ConnectionError:
        print(f"❌ Sin conexión a Convex — usando SQLite local")
        return None
    except Exception as e:
        print(f"❌ Error en query {path}: {e}")
        return None


def convex_mutation(path: str, args: dict = None):
    """Ejecuta una mutation en Convex."""
    try:
        response = requests.post(
            f"{CONVEX_URL}/api/mutation",
            json={
                "path": path,
                "args": args or {},
                "format": "json",
            },
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            print(f"❌ Error Convex mutation {path}: {data}")
            return None

        return data.get("value")

    except requests.exceptions.ConnectionError:
        print(f"❌ Sin conexión a Convex")
        return None
    except Exception as e:
        print(f"❌ Error en mutation {path}: {e}")
        return None


def test_conexion():
    """Verifica que la conexión a Convex funciona."""
    resultado = convex_query("usuarios:listar")
    if resultado is not None:
        print(f"✅ Convex conectado — {len(resultado)} usuarios")
        return True
    print("❌ Sin conexión a Convex")
    return False


if __name__ == "__main__":
    test_conexion()
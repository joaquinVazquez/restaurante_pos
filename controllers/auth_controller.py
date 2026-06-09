# controllers/auth_controller.py
from database.connection import execute_query

# Sesión en memoria
_sesion_activa = {"usuario": None}


def login(username: str, password: str):
    if not username or not password:
        return None

    resultado = execute_query("""
        SELECT id, nombre, username, password_hash, rol, activo
        FROM usuarios
        WHERE username = ? AND activo = 1
    """, [username.strip()])

    if not resultado:
        return None

    usuario = resultado[0]

    if usuario["password_hash"] == password:
        _sesion_activa["usuario"] = {
            "id":       usuario["id"],
            "nombre":   usuario["nombre"],
            "username": usuario["username"],
            "rol":      usuario["rol"]
        }
        return _sesion_activa["usuario"]

    return None


def get_sesion():
    return _sesion_activa["usuario"]


def cerrar_sesion():
    _sesion_activa["usuario"] = None


def get_modulos_permitidos(rol: str) -> list:
    if rol == "admin":
        return [
            "inicio", "ventas", "productos",
            "reportes", "caja", "clientes", "config"
        ]
    elif rol == "cajero":
        return ["inicio", "ventas", "clientes"]
    return []
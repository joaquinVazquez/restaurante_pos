# controllers/auth_controller.py
from database.db_manager import login_usuario

# Sesión en memoria
_sesion_activa = {"usuario": None}


def login(username: str, password: str):
    if not username or not password:
        return None

    usuario = login_usuario(username.strip(), password)
    if usuario:
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
            "inicio", "ventas", "productos", "inventario",
            "reportes", "caja", "clientes", "config"
        ]
    elif rol == "cajero":
        return ["inicio", "ventas", "clientes"]
    return []

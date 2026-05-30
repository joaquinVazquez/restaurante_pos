# controllers/ventas_controller.py
from database.connection import execute_query

def obtener_categorias():
    return execute_query(
        "SELECT id, nombre, icono FROM categorias WHERE activo = TRUE ORDER BY nombre"
    )

def obtener_productos(categoria_id=None, busqueda=None):
    query = """
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stock,
               c.nombre AS categoria, c.icono
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = TRUE AND p.stock > 0
    """
    params = []

    if categoria_id:
        query += " AND p.categoria_id = %s"
        params.append(categoria_id)

    if busqueda:
        query += " AND LOWER(p.nombre) LIKE LOWER(%s)"
        params.append(f"%{busqueda}%")

    query += " ORDER BY p.nombre"
    return execute_query(query, params if params else None)


class Carrito:
    def __init__(self):
        self.items = {}

    def agregar(self, producto: dict):
        pid = producto["id"]
        if pid in self.items:
            if self.items[pid]["cantidad"] < producto["stock"]:
                self.items[pid]["cantidad"] += 1
            else:
                return False, f"⚠️ Stock máximo: {producto['stock']} unidades"
        else:
            self.items[pid] = {
                "nombre":   producto["nombre"],
                "precio":   float(producto["precio"]),
                "cantidad": 1,
                "stock":    producto["stock"]
            }
        return True, "ok"

    def quitar(self, producto_id: int):
        if producto_id in self.items:
            if self.items[producto_id]["cantidad"] > 1:
                self.items[producto_id]["cantidad"] -= 1
            else:
                del self.items[producto_id]

    def vaciar(self):
        self.items = {}

    def total(self) -> float:
        return sum(v["precio"] * v["cantidad"] for v in self.items.values())

    def cantidad_items(self) -> int:
        return sum(v["cantidad"] for v in self.items.values())

    def esta_vacio(self) -> bool:
        return len(self.items) == 0
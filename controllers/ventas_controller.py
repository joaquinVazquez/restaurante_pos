# controllers/ventas_controller.py
from database.db_manager import get_categorias, get_productos


def obtener_categorias():
    return get_categorias()


def obtener_productos(categoria_id=None, busqueda=None):
    return get_productos(
        busqueda=busqueda,
        categoria_id=categoria_id
    )


class Carrito:
    def __init__(self):
        self.items = {}

    def agregar(self, producto: dict):
        pid = producto["id"]
        if pid in self.items:
            if self.items[pid]["cantidad"] < producto["stock"]:
                self.items[pid]["cantidad"] += 1
            else:
                return False, f"⚠️ Stock máximo: {producto['stock']}"
        else:
            self.items[pid] = {
                "nombre":   producto["nombre"],
                "precio":   float(producto["precio"]),
                "cantidad": 1,
                "stock":    producto["stock"]
            }
        return True, "ok"

    def quitar(self, producto_id):
        if producto_id in self.items:
            if self.items[producto_id]["cantidad"] > 1:
                self.items[producto_id]["cantidad"] -= 1
            else:
                del self.items[producto_id]

    def vaciar(self):
        self.items = {}

    def total(self) -> float:
        return sum(
            v["precio"] * v["cantidad"]
            for v in self.items.values()
        )

    def cantidad_items(self) -> int:
        return sum(v["cantidad"] for v in self.items.values())

    def esta_vacio(self) -> bool:
        return len(self.items) == 0
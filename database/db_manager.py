# database/db_manager.py
"""
Gestor de base de datos híbrido.
Usa Convex cuando hay internet, SQLite como fallback.
"""
from database.convex_client import convex_query, convex_mutation
from database.connection import execute_query as sqlite_query

# Estado de conexión
_usar_convex = {"valor": False}


def verificar_conexion():
    """Verifica si Convex está disponible."""
    resultado = convex_query("usuarios:listar")
    _usar_convex["valor"] = resultado is not None
    modo = "☁️  Convex" if _usar_convex["valor"] else "💾 SQLite"
    print(f"🔌 Modo de base de datos: {modo}")
    return _usar_convex["valor"]


def usando_convex() -> bool:
    return _usar_convex["valor"]


# ── Productos ──────────────────────────────────────────────
def get_productos(busqueda=None, categoria_id=None):
    if usando_convex():
        args = {}
        if busqueda:
            args["busqueda"] = busqueda
        if categoria_id:
            args["categoria_id"] = categoria_id
        return convex_query("productos:listar", args) or []
    else:
        query = """
            SELECT p.id, p.nombre, p.descripcion, p.precio,
                   p.stock, c.nombre AS categoria,
                   c.icono, p.activo, p.imagen
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo = 1
        """
        params = []
        if categoria_id:
            query += " AND p.categoria_id = ?"
            params.append(categoria_id)
        if busqueda:
            query += " AND LOWER(p.nombre) LIKE LOWER(?)"
            params.append(f"%{busqueda}%")
        return sqlite_query(query, params if params else None)


def crear_producto(datos: dict):
    if usando_convex():
        return convex_mutation("productos:crear", datos)
    else:
        return sqlite_query("""
            INSERT INTO productos
                (nombre, descripcion, precio, stock,
                 categoria_id, imagen)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            datos.get("nombre"),
            datos.get("descripcion"),
            datos.get("precio"),
            datos.get("stock"),
            datos.get("categoria_id"),
            datos.get("imagen"),
        ], fetch=False)


def actualizar_stock(producto_id, cantidad):
    if usando_convex():
        return convex_mutation("productos:actualizar_stock", {
            "id": producto_id,
            "cantidad": cantidad
        })
    else:
        return sqlite_query("""
            UPDATE productos SET stock = stock - ?
            WHERE id = ?
        """, [cantidad, producto_id], fetch=False)


# ── Categorías ─────────────────────────────────────────────
def get_categorias():
    if usando_convex():
        return convex_query("categorias:listar") or []
    else:
        return sqlite_query("""
            SELECT id, nombre, icono FROM categorias
            WHERE activo = 1 ORDER BY nombre
        """)


# ── Ventas ─────────────────────────────────────────────────
def crear_venta(datos: dict, items: list):
    if usando_convex():
        return convex_mutation("ventas:crear", {
            **datos,
            "items": items
        })
    else:
        resultado = sqlite_query("""
            INSERT INTO ventas
                (usuario_id, total, metodo_pago,
                 monto_recibido, cambio, estado)
            VALUES (1, ?, ?, ?, ?, 'completada')
        """, [
            datos["total"],
            datos["metodo_pago"],
            datos.get("monto_recibido"),
            datos.get("cambio"),
        ], fetch=False)

        venta_id = resultado
        for item in items:
            sqlite_query("""
                INSERT INTO detalle_ventas
                    (venta_id, producto_id, cantidad,
                     precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, [
                venta_id,
                item["producto_id"],
                item["cantidad"],
                item["precio_unitario"],
                item["subtotal"],
            ], fetch=False)

            sqlite_query("""
                UPDATE productos SET stock = stock - ?
                WHERE id = ?
            """, [item["cantidad"], item["producto_id"]],
                fetch=False)

        return venta_id


def get_resumen_dia():
    if usando_convex():
        return convex_query("ventas:resumen_dia") or {}
    else:
        resultado = sqlite_query("""
            SELECT
                COUNT(*) AS total_ventas,
                COALESCE(SUM(total), 0) AS total,
                COALESCE(SUM(CASE WHEN metodo_pago='efectivo'
                    THEN total ELSE 0 END), 0) AS efectivo,
                COALESCE(SUM(CASE WHEN metodo_pago='tarjeta'
                    THEN total ELSE 0 END), 0) AS tarjeta
            FROM ventas
            WHERE DATE(creado_en) = DATE('now')
        """)
        return resultado[0] if resultado else {}


# ── Clientes ───────────────────────────────────────────────
def get_clientes(busqueda=""):
    if usando_convex():
        return convex_query("clientes:listar",
                            {"busqueda": busqueda}) or []
    else:
        return sqlite_query("""
            SELECT * FROM clientes
            WHERE activo = 1
            AND (LOWER(nombre) LIKE LOWER(?)
                OR LOWER(telefono) LIKE LOWER(?))
            ORDER BY nombre
        """, [f"%{busqueda}%", f"%{busqueda}%"])
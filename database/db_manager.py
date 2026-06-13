# database/db_manager.py
from database.convex_client import convex_query, convex_mutation
from database.connection import execute_query as sqlite_query, get_connection

_usar_convex = {"valor": False}


def verificar_conexion():
    resultado = convex_query("usuarios:listar")
    _usar_convex["valor"] = resultado is not None
    modo = "☁️  Convex" if _usar_convex["valor"] else "💾 SQLite"
    print(f"🔌 Modo: {modo}")
    return _usar_convex["valor"]


def usando_convex() -> bool:
    return _usar_convex["valor"]


def _normalizar_producto(p: dict) -> dict:
    """Normaliza campos de Convex para que sean iguales a SQLite."""
    return {
        "id":          p.get("_id") or p.get("id"),
        "nombre":      p.get("nombre", ""),
        "descripcion": p.get("descripcion", ""),
        "precio":      float(p.get("precio", 0)),
        "stock":       int(p.get("stock", 0)),
        "categoria":   p.get("categoria", ""),
        "icono":       p.get("icono", "🍽️"),
        "activo":      p.get("activo", True),
        "imagen":      p.get("imagen"),
    }


# ── Resumen Dashboard ──────────────────────────────────────
def get_resumen_dia() -> dict:
    if usando_convex():
        r = convex_query("ventas:resumen_dia") or {}
        # Agregar productos y stock desde SQLite como complemento
        prod = sqlite_query(
            "SELECT COUNT(*) AS total FROM productos WHERE activo=1"
        )
        stock = sqlite_query(
            "SELECT COUNT(*) AS total FROM productos WHERE stock<=5 AND activo=1"
        )
        return {
            "total_ventas":      r.get("total_ventas", 0),
            "total":             r.get("total", 0),
            "efectivo":          r.get("efectivo", 0),
            "tarjeta":           r.get("tarjeta", 0),
            "productos_activos": prod[0]["total"] if prod else 0,
            "stock_bajo":        stock[0]["total"] if stock else 0,
        }
    else:
        r = sqlite_query("""
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
        prod = sqlite_query(
            "SELECT COUNT(*) AS total FROM productos WHERE activo=1"
        )
        stock = sqlite_query(
            "SELECT COUNT(*) AS total FROM productos WHERE stock<=5 AND activo=1"
        )
        base = r[0] if r else {}
        return {
            "total_ventas":      base.get("total_ventas", 0),
            "total":             base.get("total", 0),
            "efectivo":          base.get("efectivo", 0),
            "tarjeta":           base.get("tarjeta", 0),
            "productos_activos": prod[0]["total"] if prod else 0,
            "stock_bajo":        stock[0]["total"] if stock else 0,
        }


# ── Categorías ─────────────────────────────────────────────
def get_categorias():
    if usando_convex():
        cats = convex_query("categorias:listar") or []
        return [{"id": c.get("_id"), "nombre": c.get("nombre"),
                 "icono": c.get("icono", "🍽️")} for c in cats]
    else:
        return sqlite_query("""
            SELECT id, nombre, icono FROM categorias
            WHERE activo=1 ORDER BY nombre
        """) or []


# ── Productos ──────────────────────────────────────────────
def get_productos(busqueda=None, categoria_id=None):
    if usando_convex():
        args = {}
        if busqueda:      args["busqueda"]     = busqueda
        if categoria_id:  args["categoria_id"] = categoria_id
        prods = convex_query("productos:listar", args) or []
        return [_normalizar_producto(p) for p in prods
                if p.get("stock", 0) > 0]
    else:
        query = """
            SELECT p.id, p.nombre, p.descripcion, p.precio,
                   p.stock, c.nombre AS categoria,
                   c.icono, p.activo, p.imagen
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo=1 AND p.stock > 0
        """
        params = []
        if categoria_id:
            query += " AND p.categoria_id = ?"
            params.append(categoria_id)
        if busqueda:
            query += " AND LOWER(p.nombre) LIKE LOWER(?)"
            params.append(f"%{busqueda}%")
        query += " ORDER BY p.nombre"
        return sqlite_query(query, params if params else None) or []


def crear_producto(datos: dict):
    if usando_convex():
        return convex_mutation("productos:crear", datos)
    else:
        return sqlite_query("""
            INSERT INTO productos
                (nombre, descripcion, precio, stock,
                 categoria_id, imagen)
            VALUES (?,?,?,?,?,?)
        """, [
            datos.get("nombre"),
            datos.get("descripcion"),
            datos.get("precio"),
            datos.get("stock"),
            datos.get("categoria_id"),
            datos.get("imagen"),
        ], fetch=False)


def actualizar_producto(producto_id, datos: dict):
    if usando_convex():
        return convex_mutation("productos:actualizar", {
            "id": producto_id, **datos
        })
    else:
        return sqlite_query("""
            UPDATE productos
            SET nombre=?, precio=?, stock=?, categoria_id=?
            WHERE id=?
        """, [
            datos.get("nombre"),
            datos.get("precio"),
            datos.get("stock"),
            datos.get("categoria_id"),
            producto_id,
        ], fetch=False)


def desactivar_producto(producto_id):
    if usando_convex():
        return convex_mutation("productos:desactivar",
                               {"id": producto_id})
    else:
        return sqlite_query(
            "UPDATE productos SET activo=0 WHERE id=?",
            [producto_id], fetch=False
        )


def actualizar_stock(producto_id, cantidad):
    if usando_convex():
        return convex_mutation("productos:actualizar_stock", {
            "id": producto_id, "cantidad": cantidad
        })
    else:
        return sqlite_query("""
            UPDATE productos SET stock = stock - ?
            WHERE id = ?
        """, [cantidad, producto_id], fetch=False)


# ── Ventas ─────────────────────────────────────────────────
def crear_venta(datos: dict, items: list):
    if usando_convex():
        return convex_mutation("ventas:crear", {
            **datos, "items": items
        })
    else:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ventas
                    (usuario_id, total, metodo_pago,
                     monto_recibido, cambio, estado)
                VALUES (1, ?, ?, ?, ?, 'completada')
            """, [
                datos["total"],
                datos["metodo_pago"],
                datos.get("monto_recibido"),
                datos.get("cambio"),
            ])
            venta_id = cursor.lastrowid

            for item in items:
                cursor.execute("""
                    INSERT INTO detalle_ventas
                        (venta_id, producto_id, cantidad,
                         precio_unitario, subtotal)
                    VALUES (?,?,?,?,?)
                """, [
                    venta_id,
                    item["producto_id"],
                    item["cantidad"],
                    item["precio_unitario"],
                    item["subtotal"],
                ])
                cursor.execute("""
                    UPDATE productos SET stock = stock - ?
                    WHERE id = ?
                """, [item["cantidad"], item["producto_id"]])

            conn.commit()
            return venta_id
        except Exception as ex:
            conn.rollback()
            raise ex
        finally:
            conn.close()


def get_ventas(desde=None, hasta=None):
    if usando_convex():
        args = {}
        if desde: args["desde"] = str(desde)
        if hasta: args["hasta"] = str(hasta)
        return convex_query("ventas:listar", args) or []
    else:
        query = """
            SELECT v.id, v.total, v.metodo_pago,
                   v.creado_en, COUNT(dv.id) AS productos
            FROM ventas v
            LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
        """
        params = []
        if desde and hasta:
            query += " WHERE DATE(v.creado_en) BETWEEN ? AND ?"
            params = [desde, hasta]
        query += " GROUP BY v.id ORDER BY v.creado_en DESC"
        return sqlite_query(query, params if params else None) or []


# ── Clientes ───────────────────────────────────────────────
def get_clientes(busqueda=""):
    if usando_convex():
        return convex_query("clientes:listar",
                            {"busqueda": busqueda}) or []
    else:
        return sqlite_query("""
            SELECT c.id, c.nombre, c.telefono, c.email,
                   c.activo,
                   COUNT(v.id) AS total_compras,
                   COALESCE(SUM(v.total), 0) AS total_gastado
            FROM clientes c
            LEFT JOIN ventas v ON v.cliente_id = c.id
            WHERE c.activo=1
            AND (LOWER(c.nombre) LIKE LOWER(?)
                OR LOWER(COALESCE(c.telefono,'')) LIKE LOWER(?))
            GROUP BY c.id ORDER BY c.nombre
        """, [f"%{busqueda}%", f"%{busqueda}%"]) or []
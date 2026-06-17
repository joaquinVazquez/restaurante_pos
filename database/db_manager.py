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
        # ── Configuración ──────────────────────────────────────────
def get_configuracion() -> dict:
    if usando_convex():
        items = convex_query("configuracion:listar") or []
        return {i["clave"]: i["valor"] for i in items}
    else:
        items = sqlite_query(
            "SELECT clave, valor FROM configuracion"
        ) or []
        return {i["clave"]: i["valor"] for i in items}


def guardar_configuracion(datos: dict):
    claves = {
        "nombre":    "restaurante_nombre",
        "direccion": "restaurante_direccion",
        "telefono":  "restaurante_telefono",
        "email":     "restaurante_email",
        "rfc":       "restaurante_rfc",
        "logo":      "restaurante_logo",
    }
    for campo, clave in claves.items():
        valor = datos.get(campo, "")
        if usando_convex():
            convex_mutation("configuracion:guardar", {
                "clave": clave, "valor": valor
            })
        else:
            sqlite_query("""
                INSERT INTO configuracion (clave, valor)
                VALUES (?, ?)
                ON CONFLICT(clave) DO UPDATE SET valor=?
            """, [clave, valor, valor], fetch=False)


def get_config_impresora() -> dict:
    config = get_configuracion()
    return {
        "nombre_impresora": config.get("impresora_nombre", ""),
        "ancho_papel":      config.get("impresora_ancho", "80"),
        "mensaje_ticket":   config.get("ticket_mensaje",
                                       "¡Gracias por su compra!"),
    }


def guardar_config_impresora(datos: dict):
    claves = {
        "nombre_impresora": "impresora_nombre",
        "ancho_papel":      "impresora_ancho",
        "mensaje_ticket":   "ticket_mensaje",
    }
    for campo, clave in claves.items():
        valor = datos.get(campo, "")
        if usando_convex():
            convex_mutation("configuracion:guardar", {
                "clave": clave, "valor": valor
            })
        else:
            sqlite_query("""
                INSERT INTO configuracion (clave, valor)
                VALUES (?, ?)
                ON CONFLICT(clave) DO UPDATE SET valor=?
            """, [clave, valor, valor], fetch=False)


# ── Usuarios ───────────────────────────────────────────────
def get_usuarios():
    if usando_convex():
        users = convex_query("usuarios:listar") or []
        return [{
            "id":     u.get("_id"),
            "nombre": u.get("nombre"),
            "username": u.get("username"),
            "rol":    u.get("rol"),
            "activo": u.get("activo", True),
        } for u in users]
    else:
        return sqlite_query("""
            SELECT id, nombre, username, rol, activo
            FROM usuarios ORDER BY nombre
        """) or []


def crear_usuario(datos: dict):
    if usando_convex():
        return convex_mutation("usuarios:crear", {
            "nombre":        datos["nombre"],
            "username":      datos["username"],
            "password_hash": datos["password"],
            "rol":           datos.get("rol", "cajero"),
        })
    else:
        return sqlite_query("""
            INSERT INTO usuarios
                (nombre, username, password_hash, rol, activo)
            VALUES (?, ?, ?, ?, 1)
        """, [
            datos["nombre"],
            datos["username"],
            datos["password"],
            datos.get("rol", "cajero"),
        ], fetch=False)


def cambiar_password_usuario(usuario_id, password: str):
    if usando_convex():
        return convex_mutation("usuarios:cambiar_password", {
            "id": usuario_id, "password_hash": password
        })
    else:
        return sqlite_query("""
            UPDATE usuarios SET password_hash=? WHERE id=?
        """, [password, usuario_id], fetch=False)


def toggle_usuario_activo(usuario_id, activo: bool):
    if usando_convex():
        return convex_mutation("usuarios:toggle_activo", {
            "id": usuario_id, "activo": activo
        })
    else:
        return sqlite_query("""
            UPDATE usuarios SET activo=? WHERE id=?
        """, [1 if activo else 0, usuario_id], fetch=False)


# ── Categorías CRUD ────────────────────────────────────────
def crear_categoria(datos: dict):
    if usando_convex():
        return convex_mutation("categorias:crear", {
            "nombre": datos["nombre"],
            "icono":  datos.get("icono", "🍽️"),
        })
    else:
        return sqlite_query("""
            INSERT INTO categorias (nombre, icono, activo)
            VALUES (?, ?, 1)
        """, [datos["nombre"], datos.get("icono", "🍽️")],
            fetch=False)


def actualizar_categoria(categoria_id, datos: dict):
    if usando_convex():
        return convex_mutation("categorias:actualizar", {
            "id":     categoria_id,
            "nombre": datos.get("nombre"),
            "icono":  datos.get("icono"),
        })
    else:
        return sqlite_query("""
            UPDATE categorias SET nombre=?, icono=?
            WHERE id=?
        """, [datos.get("nombre"), datos.get("icono"),
              categoria_id], fetch=False)


def eliminar_categoria(categoria_id):
    # Verificar si tiene productos activos
    if usando_convex():
        prods = convex_query("productos:listar",
                             {"categoria_id": categoria_id}) or []
        if len(prods) > 0:
            raise Exception(
                "⚠️ No se puede eliminar: tiene productos activos")
        return convex_mutation("categorias:eliminar",
                               {"id": categoria_id})
    else:
        prods = sqlite_query("""
            SELECT COUNT(*) AS total FROM productos
            WHERE categoria_id=? AND activo=1
        """, [categoria_id])
        if prods and prods[0]["total"] > 0:
            raise Exception(
                "⚠️ No se puede eliminar: tiene productos activos")
        return sqlite_query(
            "UPDATE categorias SET activo=0 WHERE id=?",
            [categoria_id], fetch=False
        )
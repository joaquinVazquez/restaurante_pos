import os
from dotenv import load_dotenv
from convex import ConvexClient
from datetime import date, datetime

# 1. Cargar el .env explícitamente
load_dotenv()

# 2. Leer la URL
CONVEX_URL = os.getenv("CONVEX_URL")

if not CONVEX_URL:
    raise ValueError("La variable CONVEX_URL no está definida en el archivo .env")

# 3. Instanciar el cliente
client = ConvexClient(CONVEX_URL)

# ══════════════════ GESTIÓN DE SESIÓN (MULTI-TENANT) ══════════════════
SESION_ACTUAL = {
    "negocio_id": None,
    "usuario": None
}

def set_sesion(negocio_id: str, usuario: dict):
    SESION_ACTUAL["negocio_id"] = negocio_id
    SESION_ACTUAL["usuario"] = usuario

def cerrar_sesion():
    SESION_ACTUAL["negocio_id"] = None
    SESION_ACTUAL["usuario"] = None

def _inyectar_tenant(args: dict | None) -> dict:
    """Interceptor: Añade el negocio_id a todas las peticiones a Convex"""
    if args is None:
        args = {}
    if SESION_ACTUAL["negocio_id"]:
        args["negocio_id"] = SESION_ACTUAL["negocio_id"]
    return args
# ══════════════════════════════════════════════════════════════════════

def _required_query(path: str, args: dict | None = None):
    args_tenant = _inyectar_tenant(args)
    try:
        return client.query(path, args_tenant)
    except Exception as e:
        print(f"\n[DEBUG] Falla nativa Convex (Query '{path}'): {type(e).__name__} - {str(e)}\n")
        raise ConnectionError(f"No se pudo consultar Convex: {path}")

def _required_mutation(path: str, args: dict | None = None):
    args_tenant = _inyectar_tenant(args)
    try:
        return client.mutation(path, args_tenant)
    except Exception as e:
        print(f"\n[DEBUG] Falla nativa Convex (Mutation '{path}'): {type(e).__name__} - {str(e)}\n")
        raise ConnectionError(f"No se pudo ejecutar Convex: {path}")

def _creation_date(item: dict) -> str:
    created = item.get("_creationTime")
    if created is None:
        return item.get("fecha") or date.today().isoformat()
    return datetime.fromtimestamp(created / 1000).date().isoformat()

def verificar_conexion():
    # Solo verificamos que el cliente responda, sin requerir negocio_id
    print("Modo: Convex")
    return True

def usando_convex() -> bool:
    return True

# ── LOGIN ──
def login_usuario(username: str, password: str):
    # Usamos client.query directamente para evitar el interceptor de tenant
    # porque en el login AÚN NO tenemos un negocio_id.
    try:
        res = client.query("usuarios:login", {
            "username": username,
            "password": password,
        })
        if res and res.get("negocio_id"):
            set_sesion(res["negocio_id"], res)
        return res
    except Exception as e:
        print(f"Error en login: {e}")
        return None

def registrar_cuenta(nombre_negocio: str, nombre_usuario: str, username: str, password: str):
    try:
        res = client.mutation("usuarios:registrar_cuenta", {
            "nombre_negocio": nombre_negocio,
            "nombre_usuario": nombre_usuario,
            "username": username,
            "password": password
        })
        if res and res.get("negocio_id"):
            set_sesion(res["negocio_id"], res) # Auto-login inmediato
        return True, res
    except Exception as e:
        # Extraemos el mensaje de error de Convex de forma limpia
        error_str = str(e)
        if "El nombre de usuario ya está registrado" in error_str:
            return False, "⚠️ El nombre de usuario ya existe."
        return False, "❌ Error al crear la cuenta. Intente de nuevo."

# ── NORMALIZADORES ──
def _normalizar_categoria(c: dict) -> dict:
    return {
        "id": c.get("_id") or c.get("id"),
        "nombre": c.get("nombre", ""),
        "icono": c.get("icono", ""),
        "activo": c.get("activo", True),
    }

def _normalizar_producto(p: dict) -> dict:
    return {
        "id": p.get("_id") or p.get("id"),
        "nombre": p.get("nombre", ""),
        "descripcion": p.get("descripcion", ""),
        "precio": float(p.get("precio", 0)),
        "costo": float(p.get("costo", 0) or 0),
        "stock": int(p.get("stock", 0)),
        "categoria_id": p.get("categoria_id"),
        "categoria": p.get("categoria", ""),
        "icono": p.get("icono", ""),
        "activo": p.get("activo", True),
        "imagen": p.get("imagen"),
    }

def _normalizar_venta(v: dict) -> dict:
    return {
        "id": v.get("_id") or v.get("id"),
        "total": float(v.get("total", 0)),
        "metodo_pago": v.get("metodo_pago", ""),
        "creado_en": _creation_date(v),
        "productos": v.get("productos", 0),
        "cliente_id": v.get("cliente_id"),
    }

# ── CATÁLOGO E INVENTARIO ──
def get_categorias():
    return [_normalizar_categoria(c) for c in (_required_query("categorias:listar") or [])]

def get_productos(busqueda=None, categoria_id=None, include_sin_stock=False):
    args = {}
    if busqueda:
        args["busqueda"] = busqueda
    if categoria_id:
        args["categoria_id"] = categoria_id

    categorias = {c["id"]: c for c in get_categorias()}
    productos = []
    for p in _required_query("productos:listar", args) or []:
        producto = _normalizar_producto(p)
        cat = categorias.get(producto["categoria_id"], {})
        producto["categoria"] = cat.get("nombre", "")
        producto["icono"] = cat.get("icono", producto.get("icono", ""))
        if include_sin_stock or producto["stock"] > 0:
            productos.append(producto)
    return productos

def crear_producto(datos: dict):
    payload = {
        "nombre": datos.get("nombre"),
        "descripcion": datos.get("descripcion") or "",
        "precio": float(datos.get("precio", 0)),
        "stock": int(datos.get("stock", 0)),
    }
    if datos.get("categoria_id"):
        payload["categoria_id"] = datos["categoria_id"]
    if datos.get("imagen"):
        payload["imagen"] = datos["imagen"]
    return _required_mutation("productos:crear", payload)

def actualizar_producto(producto_id, datos: dict):
    payload = {"id": producto_id}
    # Añadimos "activo" a la lista de llaves permitidas
    for key in ("nombre", "descripcion", "categoria_id", "imagen", "activo"):
        if key in datos and datos.get(key) is not None:
            payload[key] = datos.get(key)
    if "precio" in datos:
        payload["precio"] = float(datos["precio"])
    if "stock" in datos:
        payload["stock"] = int(datos["stock"])
    return _required_mutation("productos:actualizar", payload)

def desactivar_producto(producto_id: str):
    """Realiza un borrado lógico ocultando el producto del catálogo"""
    return actualizar_producto(producto_id, {"activo": False})


def actualizar_stock(producto_id, cantidad):
    return _required_mutation("productos:actualizar_stock", {
        "id": producto_id,
        "cantidad": float(cantidad),
    })

def crear_categoria(datos: dict):
    payload = {"nombre": datos["nombre"]}
    if datos.get("icono"):
        payload["icono"] = datos["icono"]
    return _required_mutation("categorias:crear", payload)

# ── VENTAS Y REPORTES ──
def crear_venta(datos: dict, items: list):
    return _required_mutation("ventas:crear", {**datos, "items": items})

def get_ventas(desde=None, hasta=None):
    args = {}
    if desde: args["desde"] = str(desde)
    if hasta: args["hasta"] = str(hasta)
    return [_normalizar_venta(v) for v in (_required_query("ventas:listar", args) or [])]

def get_resumen_dia() -> dict:
    resumen = _required_query("ventas:resumen_dia") or {}
    productos = get_productos(include_sin_stock=True)
    return {
        "total_ventas": resumen.get("total_ventas", 0),
        "total": resumen.get("total", 0),
        "efectivo": resumen.get("efectivo", 0),
        "tarjeta": resumen.get("tarjeta", 0),
        "productos_activos": len([p for p in productos if p.get("activo", True)]),
        "stock_bajo": len([p for p in productos if p.get("activo", True) and int(p.get("stock", 0)) <= 5]),
    }

def get_reporte_ventas(desde: str, hasta: str) -> dict:
    ventas = get_ventas(desde, hasta)
    total = sum(v.get("total", 0) for v in ventas)
    efectivo = sum(v.get("total", 0) for v in ventas if v.get("metodo_pago") == "efectivo")
    tarjeta = sum(v.get("total", 0) for v in ventas if v.get("metodo_pago") == "tarjeta")
    return {"ingresos": total, "cantidad_ventas": len(ventas), "efectivo": efectivo, "tarjeta": tarjeta}

def get_reporte_margen(desde: str, hasta: str) -> dict:
    ventas = _required_query("ventas:listar", {"desde": desde, "hasta": hasta}) or []
    ingresos = sum(v.get("total", 0) for v in ventas)
    gastos = sum(g.get("monto", 0) for g in get_gastos(desde, hasta))
    merma = sum(m.get("costo_total", 0) for m in get_mermas(desde, hasta))

    venta_ids = [v["id"] for v in ventas if v.get("id")]
    costo_productos = _required_query(
        "detalle_ventas:costo_total_periodo", {"venta_ids": venta_ids}
    ) if venta_ids else 0

    ganancia_neta = ingresos - costo_productos - gastos - merma
    margen_pct = (ganancia_neta / ingresos * 100) if ingresos else 0
    return {
        "ingresos": ingresos,
        "costo_productos": costo_productos,
        "gastos": gastos,
        "merma": merma,
        "ganancia_neta": ganancia_neta,
        "margen_pct": margen_pct,
    }

# ── GASTOS, MERMAS Y CAJA ──
def get_gastos(desde: str, hasta: str):
    return _required_query("gastos:listar", {"desde": desde, "hasta": hasta}) or []

def crear_gasto(datos: dict):
    return _required_mutation("gastos:crear", {
        "categoria": datos["categoria"], "descripcion": datos["descripcion"],
        "monto": float(datos["monto"]), "fecha": datos["fecha"]
    })

def get_mermas(desde: str, hasta: str):
    return _required_query("mermas:listar", {"desde": desde, "hasta": hasta}) or []

def crear_merma(datos: dict):
    return _required_mutation("mermas:crear", {
        "producto_id": datos["producto_id"], "cantidad": float(datos["cantidad"]),
        "motivo": datos["motivo"], "fecha": datos["fecha"]
    })

def get_cortes_caja(desde: str | None = None, hasta: str | None = None):
    args = {}
    if desde: args["desde"] = str(desde)
    if hasta: args["hasta"] = str(hasta)
    cortes = _required_query("cortes_caja:listar", args) or []
    return [{"id": c.get("_id") or c.get("id"), **c} for c in cortes]

def crear_corte_caja(datos: dict):
    payload = {
        "fecha": datos.get("fecha", str(date.today())),
        "fondo_inicial": float(datos.get("fondo_inicial", 0)),
        "total_ventas": float(datos.get("total_ventas", 0)),
        "total_ingresos": float(datos.get("total_ingresos", 0)),
        "diferencia": float(datos.get("diferencia", 0)),
    }
    if "observaciones" in datos and datos["observaciones"]:
        payload["observaciones"] = datos["observaciones"]
        
    return _required_mutation("cortes_caja:crear", payload)

def get_comparativa(periodo: str):
    ventas = get_ventas()
    totales = {}
    for venta in ventas:
        fecha = venta["creado_en"]
        grupo = str(datetime.fromisoformat(fecha).weekday()) if periodo == "semanal" else (fecha[-2:] if periodo == "mensual" else fecha[5:7])
        totales[grupo] = totales.get(grupo, 0) + venta.get("total", 0)
    return [{"grupo": k, "total": v} for k, v in sorted(totales.items())]

# ── GESTIÓN DE CLIENTES ──
def get_clientes(busqueda=None):
    args = {}
    if busqueda:
        args["busqueda"] = busqueda
    
    clientes = _required_query("clientes:listar", args) or []
    # Normalización básica para estandarizar el ID en Flet
    return [{"id": c.get("_id") or c.get("id"), **c} for c in clientes]

def crear_cliente(datos: dict):
    payload = {
        "nombre": datos["nombre"],
    }
    if datos.get("telefono"): payload["telefono"] = datos["telefono"]
    if datos.get("email"): payload["email"] = datos["email"]
    
    return _required_mutation("clientes:crear", payload)

def actualizar_cliente(cliente_id: str, datos: dict):
    payload = {"id": cliente_id}
    for key in ("nombre", "telefono", "email"):
        if key in datos and datos.get(key) is not None:
            payload[key] = datos.get(key)
            
    return _required_mutation("clientes:actualizar", payload)

def desactivar_cliente(cliente_id: str):
    """Elimina físicamente al cliente de la base de datos del inquilino"""
    return _required_mutation("clientes:eliminar", {"id": cliente_id})

def get_historial_cliente(cliente_id: str):
    """Obtiene las ventas vinculadas a un cliente específico"""
    return _required_query("ventas:listar_por_cliente", {"cliente_id": cliente_id})

# ── CONFIGURACIÓN DEL RESTAURANTE ──
def get_configuracion():
    return _required_query("configuracion:listar") or {}

def guardar_configuracion(datos: dict):
    payload = {}
    for key in ("nombre_restaurante", "direccion", "telefono", "email", "rfc", "mensaje_ticket", "logo"):
        if key in datos and datos.get(key) is not None:
            payload[key] = datos[key]
    return _required_mutation("configuracion:guardar", payload)

# ── CONFIGURACIÓN DE IMPRESORA ──
def get_config_impresora():
    return _required_query("configuracion:listar_impresora") or {}

def guardar_config_impresora(datos: dict):
    payload = {"ancho_papel": datos.get("ancho_papel", "80")}
    if datos.get("nombre_impresora"):
        payload["nombre_impresora"] = datos["nombre_impresora"]
    if datos.get("mensaje_ticket"):
        payload["mensaje_ticket"] = datos["mensaje_ticket"]
    return _required_mutation("configuracion:guardar_impresora", payload)

# ── GESTIÓN DE USUARIOS ──
def get_usuarios():
    usuarios = _required_query("configuracion:listar_usuarios") or []
    return [{"id": u.get("_id") or u.get("id"), **u} for u in usuarios]

def crear_usuario(datos: dict):
    return _required_mutation("configuracion:crear_usuario", {
        "nombre": datos["nombre"],
        "username": datos["username"],
        "password": datos["password"],
        "rol": datos.get("rol", "cajero"),
    })

def cambiar_password_usuario(usuario_id: str, password: str):
    return _required_mutation("configuracion:cambiar_password", {
        "id": usuario_id,
        "password": password,
    })

def toggle_usuario_activo(usuario_id: str, activo: bool):
    return _required_mutation("configuracion:toggle_activo", {
        "id": usuario_id,
        "activo": activo,
    })

# ── GESTIÓN DE CATEGORÍAS (edición/borrado) ──
def actualizar_categoria(categoria_id: str, datos: dict):
    payload = {"id": categoria_id}
    for key in ("nombre", "icono", "activo"):
        if key in datos and datos.get(key) is not None:
            payload[key] = datos[key]
    return _required_mutation("configuracion:actualizar_categoria", payload)

def eliminar_categoria(categoria_id: str):
    return _required_mutation("configuracion:eliminar_categoria", {"id": categoria_id})

# ── DETALLE DE VENTAS ──
def get_detalle_venta(venta_id: str):
    detalles = _required_query("detalle_ventas:listar_por_venta", {"venta_id": venta_id}) or []
    return [
        {
            "producto_nombre": d.get("producto_nombre", "Producto eliminado"),
            "cantidad": d.get("cantidad", 0),
            "precio_unitario": float(d.get("precio_unitario", 0)),
            "subtotal": float(d.get("subtotal", 0)),
        }
        for d in detalles
    ]

# ── INVENTARIO (ENTRADAS / COMPRAS) ──
def get_entradas_inventario(desde: str, hasta: str):
    entradas = _required_query("inventario:listar", {"desde": desde, "hasta": hasta}) or []
    return [
        {
            "id": e.get("_id") or e.get("id"),
            "producto_nombre": e.get("producto_nombre", "—"),
            "cantidad": e.get("cantidad", 0),
            "costo_unitario": float(e.get("costo_unitario", 0)),
            "costo_total": float(e.get("costo_total", 0)),
            "proveedor": e.get("proveedor", ""),
            "fecha": e.get("fecha", ""),
        }
        for e in entradas
    ]

def crear_entrada_inventario(datos: dict):
    payload = {
        "producto_id": datos["producto_id"],
        "cantidad": float(datos["cantidad"]),
        "costo_unitario": float(datos["costo_unitario"]),
        "fecha": datos["fecha"],
        "actualizar_costo_producto": bool(datos.get("actualizar_costo_producto", False)),
    }
    if datos.get("proveedor"):
        payload["proveedor"] = datos["proveedor"]
    return _required_mutation("inventario:crear", payload)

# ── PRODUCTOS MÁS VENDIDOS ──
def get_productos_mas_vendidos(desde: str, hasta: str, limite: int = 10):
    ventas = get_ventas(desde, hasta)
    venta_ids = [v["id"] for v in ventas if v.get("id")]
    if not venta_ids:
        return []
    resultado = _required_query(
        "detalle_ventas:productos_mas_vendidos",
        {"venta_ids": venta_ids}
    ) or []
    return resultado[:limite]
import os
from dotenv import load_dotenv
from convex import ConvexClient
from datetime import date, datetime

# SE ELIMINÓ LA IMPORTACIÓN DE convex_client PORQUE ES REDUNDANTE Y ENMASCARA ERRORES
# from database.convex_client import convex_mutation, convex_query

# 1. Cargar el .env explícitamente
load_dotenv()

# 2. Leer la URL
CONVEX_URL = os.getenv("CONVEX_URL")

if not CONVEX_URL:
    raise ValueError("La variable CONVEX_URL no está definida en el archivo .env")

# 3. Instanciar el cliente
client = ConvexClient(CONVEX_URL)


def _required_query(path: str, args: dict | None = None):
    try:
        # Se ejecuta directamente sobre el cliente local validado
        result = client.query(path, args)
        return result
    except Exception as e:
        # Trazabilidad estricta sin Exception Swallowing
        print(f"\n[DEBUG] Falla nativa Convex (Query '{path}'): {type(e).__name__} - {str(e)}\n")
        raise ConnectionError(f"No se pudo consultar Convex: {path}")


def _required_mutation(path: str, args: dict | None = None):
    try:
        # Se ejecuta directamente sobre el cliente local validado
        result = client.mutation(path, args)
        return result
    except Exception as e:
        # Trazabilidad estricta sin Exception Swallowing
        print(f"\n[DEBUG] Falla nativa Convex (Mutation '{path}'): {type(e).__name__} - {str(e)}\n")
        raise ConnectionError(f"No se pudo ejecutar Convex: {path}")


def _creation_date(item: dict) -> str:
    created = item.get("_creationTime")
    if created is None:
        return item.get("fecha") or date.today().isoformat()
    return datetime.fromtimestamp(created / 1000).date().isoformat()


def verificar_conexion():
    _required_query("usuarios:listar")
    print("Modo: Convex")
    return True


def usando_convex() -> bool:
    return True


def login_usuario(username: str, password: str):
    return _required_query("usuarios:login", {
        "username": username,
        "password": password,
    })


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


def get_resumen_dia() -> dict:
    resumen = _required_query("ventas:resumen_dia") or {}
    productos = get_productos(include_sin_stock=True)
    return {
        "total_ventas": resumen.get("total_ventas", 0),
        "total": resumen.get("total", 0),
        "efectivo": resumen.get("efectivo", 0),
        "tarjeta": resumen.get("tarjeta", 0),
        "productos_activos": len([p for p in productos if p.get("activo", True)]),
        "stock_bajo": len([
            p for p in productos
            if p.get("activo", True) and int(p.get("stock", 0)) <= 5
        ]),
    }


def get_categorias():
    return [_normalizar_categoria(c)
            for c in (_required_query("categorias:listar") or [])]


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
    return _required_mutation("productos:crear", {
        "nombre": datos.get("nombre"),
        "descripcion": datos.get("descripcion") or "",
        "precio": float(datos.get("precio", 0)),
        "stock": int(datos.get("stock", 0)),
        "categoria_id": datos.get("categoria_id") or None,
        "imagen": datos.get("imagen") or None,
    })


def actualizar_producto(producto_id, datos: dict):
    payload = {"id": producto_id}
    for key in ("nombre", "descripcion", "categoria_id", "imagen"):
        if key in datos:
            payload[key] = datos.get(key) or None
    if "precio" in datos:
        payload["precio"] = float(datos["precio"])
    if "stock" in datos:
        payload["stock"] = int(datos["stock"])
    return _required_mutation("productos:actualizar", payload)


def desactivar_producto(producto_id):
    return _required_mutation("productos:desactivar", {"id": producto_id})


def actualizar_stock(producto_id, cantidad):
    return _required_mutation("productos:actualizar_stock", {
        "id": producto_id,
        "cantidad": float(cantidad),
    })


def crear_venta(datos: dict, items: list):
    return _required_mutation("ventas:crear", {**datos, "items": items})


def get_ventas(desde=None, hasta=None):
    args = {}
    if desde:
        args["desde"] = str(desde)
    if hasta:
        args["hasta"] = str(hasta)
    return [_normalizar_venta(v) for v in (_required_query("ventas:listar", args) or [])]


def get_clientes(busqueda=""):
    clientes = _required_query("clientes:listar", {"busqueda": busqueda or ""}) or []
    ventas = get_ventas()
    salida = []
    for c in clientes:
        cid = c.get("_id")
        compras = [v for v in ventas if v.get("cliente_id") == cid]
        salida.append({
            "id": cid,
            "nombre": c.get("nombre", ""),
            "telefono": c.get("telefono"),
            "email": c.get("email"),
            "direccion": c.get("direccion"),
            "notas": c.get("notas"),
            "activo": c.get("activo", True),
            "total_compras": len(compras),
            "total_gastado": sum(v.get("total", 0) for v in compras),
        })
    return salida


def crear_cliente(datos: dict):
    return _required_mutation("clientes:crear", datos)


def actualizar_cliente(cliente_id, datos: dict):
    return _required_mutation("clientes:actualizar", {"id": cliente_id, **datos})


def desactivar_cliente(cliente_id):
    return _required_mutation("clientes:desactivar", {"id": cliente_id})


def get_historial_cliente(cliente_id):
    return _required_query("clientes:historial", {"cliente_id": cliente_id}) or []


def get_configuracion() -> dict:
    items = _required_query("configuracion:listar") or []
    return {i["clave"]: i.get("valor", "") for i in items}


def guardar_configuracion(datos: dict):
    claves = {
        "nombre": "restaurante_nombre",
        "direccion": "restaurante_direccion",
        "telefono": "restaurante_telefono",
        "email": "restaurante_email",
        "rfc": "restaurante_rfc",
        "logo": "restaurante_logo",
    }
    for campo, clave in claves.items():
        if campo in datos:
            _required_mutation("configuracion:guardar", {
                "clave": clave,
                "valor": datos.get(campo, ""),
            })


def get_config_impresora() -> dict:
    config = get_configuracion()
    return {
        "nombre_impresora": config.get("impresora_nombre", ""),
        "ancho_papel": config.get("impresora_ancho", "80"),
        "mensaje_ticket": config.get("ticket_mensaje", "Gracias por su compra!"),
    }


def guardar_config_impresora(datos: dict):
    claves = {
        "nombre_impresora": "impresora_nombre",
        "ancho_papel": "impresora_ancho",
        "mensaje_ticket": "ticket_mensaje",
    }
    for campo, clave in claves.items():
        _required_mutation("configuracion:guardar", {
            "clave": clave,
            "valor": datos.get(campo, ""),
        })


def get_usuarios():
    return [{
        "id": u.get("_id"),
        "nombre": u.get("nombre"),
        "username": u.get("username"),
        "rol": u.get("rol"),
        "activo": u.get("activo", True),
    } for u in (_required_query("usuarios:listar") or [])]


def crear_usuario(datos: dict):
    return _required_mutation("usuarios:crear", {
        "nombre": datos["nombre"],
        "username": datos["username"],
        "password_hash": datos["password"],
        "rol": datos.get("rol", "cajero"),
    })


def cambiar_password_usuario(usuario_id, password: str):
    return _required_mutation("usuarios:cambiar_password", {
        "id": usuario_id,
        "password_hash": password,
    })


def toggle_usuario_activo(usuario_id, activo: bool):
    return _required_mutation("usuarios:toggle_activo", {
        "id": usuario_id,
        "activo": activo,
    })


def crear_categoria(datos: dict):
    return _required_mutation("categorias:crear", {
        "nombre": datos["nombre"],
        "icono": datos.get("icono", ""),
    })


def actualizar_categoria(categoria_id, datos: dict):
    return _required_mutation("categorias:actualizar", {
        "id": categoria_id,
        "nombre": datos.get("nombre"),
        "icono": datos.get("icono"),
    })


def eliminar_categoria(categoria_id):
    prods = get_productos(categoria_id=categoria_id, include_sin_stock=True)
    if prods:
        raise Exception("No se puede eliminar: tiene productos activos")
    return _required_mutation("categorias:eliminar", {"id": categoria_id})


def get_reporte_ventas(desde: str, hasta: str) -> dict:
    ventas = get_ventas(desde, hasta)
    total = sum(v.get("total", 0) for v in ventas)
    efectivo = sum(v.get("total", 0) for v in ventas
                   if v.get("metodo_pago") == "efectivo")
    tarjeta = sum(v.get("total", 0) for v in ventas
                  if v.get("metodo_pago") == "tarjeta")
    return {
        "ingresos": total,
        "cantidad_ventas": len(ventas),
        "efectivo": efectivo,
        "tarjeta": tarjeta,
    }


def get_reporte_margen(desde: str, hasta: str) -> dict:
    ventas = _required_query("ventas:listar", {"desde": desde, "hasta": hasta}) or []
    ingresos = sum(v.get("total", 0) for v in ventas)
    gastos = sum(g.get("monto", 0) for g in get_gastos(desde, hasta))
    merma = sum(m.get("costo_total", 0) for m in get_mermas(desde, hasta))
    costo_productos = 0
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


def get_gastos(desde: str, hasta: str):
    return _required_query("gastos:listar", {"desde": desde, "hasta": hasta}) or []


def crear_gasto(datos: dict):
    return _required_mutation("gastos:crear", {
        "categoria": datos["categoria"],
        "descripcion": datos["descripcion"],
        "monto": float(datos["monto"]),
        "fecha": datos["fecha"],
    })


def get_mermas(desde: str, hasta: str):
    return _required_query("mermas:listar", {"desde": desde, "hasta": hasta}) or []


def crear_merma(datos: dict):
    return _required_mutation("mermas:crear", {
        "producto_id": datos["producto_id"],
        "cantidad": float(datos["cantidad"]),
        "motivo": datos["motivo"],
        "fecha": datos["fecha"],
    })


def get_comparativa(periodo: str):
    ventas = get_ventas()
    totales = {}
    for venta in ventas:
        fecha = venta["creado_en"]
        if periodo == "semanal":
            grupo = str(datetime.fromisoformat(fecha).weekday())
        elif periodo == "mensual":
            grupo = fecha[-2:]
        else:
            grupo = fecha[5:7]
        totales[grupo] = totales.get(grupo, 0) + venta.get("total", 0)
    return [{"grupo": k, "total": v} for k, v in sorted(totales.items())]


def get_caja_hoy():
    resumen = get_resumen_dia()
    return [{
        "total_ventas": resumen["total_ventas"],
        "total_ingresos": resumen["total"],
        "efectivo": resumen["efectivo"],
        "tarjeta": resumen["tarjeta"],
    }]


def crear_corte_caja(datos: dict):
    return _required_mutation("cortes_caja:crear", datos)


def get_cortes_caja(desde: str | None = None, hasta: str | None = None):
    args = {}
    if desde:
        args["desde"] = str(desde)
    if hasta:
        args["hasta"] = str(hasta)
    return _required_query("cortes_caja:listar", args) or []

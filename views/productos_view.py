# views/productos_view.py
import flet as ft
import shutil
import os
from database.db_manager import (
    actualizar_producto,
    crear_producto,
    desactivar_producto,
    get_categorias,
    get_productos,
)

COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#ffffff"
COLOR_ACENTO     = "#00b894"
COLOR_ROJO       = "#e74c3c"
COLOR_AZUL       = "#3498db"
COLOR_NARANJA    = "#ff7a00"
COLOR_FONDO      = "#f0f4f8"

RUTA_IMAGENES = "assets/productos"


def productos_view(page: ft.Page):

    def cargar_productos(busqueda=""):
        return get_productos(busqueda=busqueda, include_sin_stock=True)

    def cargar_categorias():
        return get_categorias()

    imagen_seleccionada = {"ruta": None}

    preview_imagen = ft.Container(
        content=ft.Text("Sin imagen", color=COLOR_SUBTEXTO, size=12),
        width=100,
        height=100,
        bgcolor=COLOR_FONDO,
        border_radius=10,
        alignment=ft.alignment.center,
        border=ft.border.all(1, "#e0e0e0")
    )

    def seleccionar_imagen(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            archivo = e.files[0]
            ruta_origen = archivo.path
            nombre_base = campo_nombre.value.strip().replace(" ", "_") or "producto"
            nombre_archivo = f"{nombre_base}_{archivo.name}"
            ruta_destino = os.path.join(RUTA_IMAGENES, nombre_archivo)
            os.makedirs(RUTA_IMAGENES, exist_ok=True)
            shutil.copy2(ruta_origen, ruta_destino)
            imagen_seleccionada["ruta"] = ruta_destino
            preview_imagen.content = ft.Image(
                src=ruta_destino,
                width=100,
                height=100,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(10)
            )
            page.update()

    file_picker = ft.FilePicker(on_result=seleccionar_imagen)
    page.overlay.append(file_picker)

    # ── Tabla ──────────────────────────────────────────────
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Categoría", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Stock", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, "#e0e0e0"),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, "#f0f0f0"),
        heading_row_color="#f8f9fa",
        heading_row_height=48,
        data_row_min_height=60,
        expand=True,
    )

    def hacer_imagen_tabla(ruta):
        if ruta and os.path.exists(ruta):
            return ft.Container(
                content=ft.Image(
                    src=ruta,
                    width=45,
                    height=45,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(8)
                ),
                width=45,
                height=45,
                border_radius=8,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
        return ft.Container(
            content=ft.Text("🍽️", size=22),
            width=45,
            height=45,
            bgcolor=COLOR_FONDO,
            border_radius=8,
            alignment=ft.alignment.center
        )

    def refrescar_tabla(busqueda=""):
        productos = cargar_productos(busqueda)
        tabla.rows.clear()
        for p in productos:
            stock_color = COLOR_ROJO if p["stock"] <= 5 else COLOR_ACENTO
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(hacer_imagen_tabla(p["imagen"])),
                        ft.DataCell(
                            ft.Text(p["nombre"], size=13,
                                    color=COLOR_TEXTO,
                                    weight=ft.FontWeight.W_500)
                        ),
                        ft.DataCell(
                            ft.Text(p["categoria"] or "—",
                                    size=12, color=COLOR_SUBTEXTO)
                        ),
                        ft.DataCell(
                            ft.Text(f"${p['precio']:.2f}",
                                    size=13, color=COLOR_TEXTO)
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    f"{p['stock']} uds",
                                    size=11, color="white",
                                    weight=ft.FontWeight.BOLD
                                ),
                                bgcolor=stock_color,
                                border_radius=20,
                                padding=ft.padding.symmetric(
                                    horizontal=10, vertical=4)
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    "Activo" if p["activo"] else "Inactivo",
                                    size=11, color="white"
                                ),
                                bgcolor=COLOR_ACENTO if p["activo"] else COLOR_ROJO,
                                border_radius=20,
                                padding=ft.padding.symmetric(
                                    horizontal=10, vertical=4)
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.TextButton(
                                        "✏️ Editar",
                                        on_click=lambda e, prod=p: abrir_editar(prod)
                                    ),
                                    ft.TextButton(
                                        "🗑️",
                                        on_click=lambda e, prod=p: confirmar_eliminar(prod),
                                        style=ft.ButtonStyle(color=COLOR_ROJO)
                                    ),
                                ],
                                spacing=0
                            )
                        ),
                    ]
                )
            )
        page.update()

    # ── Campos del diálogo ─────────────────────────────────
    campo_nombre   = ft.TextField(label="Nombre del producto",
                                   border_radius=8, expand=True)
    campo_precio   = ft.TextField(label="Precio de venta", prefix_text="$",
                                   border_radius=8, width=150,
                                   keyboard_type=ft.KeyboardType.NUMBER)
    campo_costo    = ft.TextField(label="Costo", prefix_text="$",
                                   hint_text="Lo que te cuesta a ti",
                                   border_radius=8, width=150,
                                   keyboard_type=ft.KeyboardType.NUMBER)
    campo_stock    = ft.TextField(label="Stock",
                                   border_radius=8, width=150,
                                   keyboard_type=ft.KeyboardType.NUMBER)
    campo_desc     = ft.TextField(label="Descripción (opcional)",
                                   border_radius=8, multiline=True,
                                   min_lines=2, max_lines=3, expand=True)
    dd_categoria   = ft.Dropdown(label="Categoría",
                                  border_radius=8, expand=True)
    titulo_dialogo = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
    producto_editando = {"id": None}

    def cargar_dd_categorias():
        dd_categoria.options.clear()
        for c in cargar_categorias():
            dd_categoria.options.append(
                ft.dropdown.Option(key=str(c["id"]), text=c["nombre"])
            )

    dialogo = ft.AlertDialog(
        modal=True,
        title=titulo_dialogo,
        content=ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(controls=[campo_nombre]),
                    ft.Row(controls=[campo_precio, campo_costo], spacing=12),
                    ft.Row(controls=[campo_stock, dd_categoria], spacing=12),
                    ft.Row(controls=[campo_desc]),
                    ft.Divider(),
                    ft.Text("Imagen del producto", size=13,
                            color=COLOR_TEXTO, weight=ft.FontWeight.BOLD),
                    ft.Text("Formatos: JPG, PNG, WEBP",
                            size=11, color=COLOR_SUBTEXTO),
                    ft.Row(
                        controls=[
                            preview_imagen,
                            ft.Container(width=16),
                            ft.ElevatedButton(
                                "📁 Seleccionar imagen",
                                bgcolor=COLOR_AZUL,
                                color="white",
                                on_click=lambda e: file_picker.pick_files(
                                    allowed_extensions=["jpg", "jpeg",
                                                        "png", "webp"]
                                )
                            )
                        ],
                    ),
                ],
                spacing=12,
                tight=True
            ),
            width=460,
            height=470,
            padding=10
        ),
        actions=[
            ft.TextButton("Cancelar",
                          on_click=lambda e: cerrar_dialogo()),
            ft.ElevatedButton(
                "Guardar",
                bgcolor=COLOR_ACENTO,
                color="white",
                on_click=lambda e: guardar_producto()
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def abrir_agregar(e):
        titulo_dialogo.value    = "➕ Agregar Producto"
        producto_editando["id"] = None
        imagen_seleccionada["ruta"] = None
        campo_nombre.value  = ""
        campo_precio.value  = ""
        campo_costo.value   = ""
        campo_stock.value   = ""
        campo_desc.value    = ""
        dd_categoria.value  = None
        preview_imagen.content = ft.Text("Sin imagen",
                                          color=COLOR_SUBTEXTO, size=12)
        cargar_dd_categorias()
        if dialogo not in page.overlay:
            page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def abrir_editar(prod):
        titulo_dialogo.value    = "✏️ Editar Producto"
        producto_editando["id"] = prod["id"]
        imagen_seleccionada["ruta"] = prod["imagen"]
        campo_nombre.value  = prod["nombre"]
        campo_precio.value  = str(prod["precio"])
        campo_costo.value   = str(prod.get("costo", 0) or "")
        campo_stock.value   = str(prod["stock"])
        campo_desc.value    = ""
        dd_categoria.value  = None
        if prod["imagen"] and os.path.exists(str(prod["imagen"])):
            preview_imagen.content = ft.Image(
                src=prod["imagen"],
                width=100, height=100,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(10)
            )
        else:
            preview_imagen.content = ft.Text("Sin imagen",
                                              color=COLOR_SUBTEXTO, size=12)
        cargar_dd_categorias()
        if dialogo not in page.overlay:
            page.overlay.append(dialogo)
        dialogo.open = True
        page.update()


    def cerrar_dialogo():
        dialogo.open = False
        page.update()

    def guardar_producto():
        nombre = campo_nombre.value.strip()
        precio = campo_precio.value.strip()
        costo  = campo_costo.value.strip()
        stock  = campo_stock.value.strip()

        if not nombre or not precio or not stock:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    "⚠️ Nombre, precio y stock son obligatorios",
                    color="white"),
                bgcolor=COLOR_NARANJA
            )
            page.snack_bar.open = True
            page.update()
            return

        try:
            precio_f = float(precio)
            costo_f  = float(costo) if costo else 0.0
            stock_i  = int(stock)
            cat_id   = str(dd_categoria.value) if dd_categoria.value else None
            imagen   = imagen_seleccionada["ruta"]

            if producto_editando["id"]:
                actualizar_producto(producto_editando["id"], {
                    "nombre": nombre,
                    "precio": precio_f,
                    "costo": costo_f,
                    "stock": stock_i,
                    "categoria_id": cat_id,
                    "imagen": imagen,
                })
                msg = "✅ Producto actualizado"
            else:
                crear_producto({
                    "nombre": nombre,
                    "precio": precio_f,
                    "costo": costo_f,
                    "stock": stock_i,
                    "categoria_id": cat_id,
                    "imagen": imagen,
                })
                msg = "✅ Producto agregado"

            cerrar_dialogo()
            refrescar_tabla()
            page.snack_bar = ft.SnackBar(
                content=ft.Text(msg, color="white"),
                bgcolor=COLOR_ACENTO
            )
            page.snack_bar.open = True
            page.update()

        except ValueError:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    "⚠️ Precio y stock deben ser números",
                    color="white"),
                bgcolor=COLOR_NARANJA
            )
            page.snack_bar.open = True
            page.update()

    # ── Eliminar ───────────────────────────────────────────
    dialogo_eliminar = ft.AlertDialog(
        modal=True,
        title=ft.Text("🗑️ Eliminar producto"),
        content=ft.Text(
            "¿Estás seguro? El producto será desactivado."),
        actions=[
            ft.TextButton("Cancelar",
                          on_click=lambda e: cerrar_eliminar()),
            ft.ElevatedButton(
                "Eliminar", bgcolor=COLOR_ROJO, color="white",
                on_click=lambda e: ejecutar_eliminar()
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    producto_a_eliminar = {"id": None}

    def confirmar_eliminar(prod):
        producto_a_eliminar["id"] = prod["id"]
        if dialogo_eliminar not in page.overlay:
            page.overlay.append(dialogo_eliminar)
        dialogo_eliminar.open = True
        page.update()

    def cerrar_eliminar():
        dialogo_eliminar.open = False
        page.update()

    def ejecutar_eliminar():
        desactivar_producto(producto_a_eliminar["id"])
        cerrar_eliminar()
        refrescar_tabla()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("🗑️ Producto desactivado", color="white"),
            bgcolor=COLOR_ROJO
        )
        page.snack_bar.open = True
        page.update()

    # ── Búsqueda ───────────────────────────────────────────
    campo_busqueda = ft.TextField(
        hint_text="🔍 Buscar por nombre o categoría...",
        on_change=lambda e: refrescar_tabla(e.control.value),
        border_radius=8,
        height=42,
        expand=True,
        bgcolor="white"
    )

    refrescar_tabla()

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("📦 Productos", size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_TEXTO),
                            ft.Text("Gestiona tu menú",
                                    size=13, color=COLOR_SUBTEXTO),
                        ],
                        spacing=2
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "➕ Agregar Producto",
                        bgcolor=COLOR_ACENTO,
                        color="white",
                        height=42,
                        on_click=abrir_agregar
                    ),
                ],
            ),
            ft.Container(height=8),
            ft.Row(controls=[campo_busqueda]),
            ft.Container(height=8),
            ft.Container(
                content=ft.ListView(
                    controls=[tabla],
                    expand=True,
                ),
                bgcolor=COLOR_TARJETA,
                border_radius=12,
                padding=8,
                expand=True,
                shadow=ft.BoxShadow(
                    blur_radius=8,
                    color="#00000010",
                    offset=ft.Offset(0, 2)
                )
            )
        ],
        expand=True,
        spacing=0
    )

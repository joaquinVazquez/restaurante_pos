# views/inventario_view.py
import flet as ft
from datetime import date
from database.db_manager import (
    get_entradas_inventario, crear_entrada_inventario,
    get_productos,
)

COLOR_TEXTO    = "#2c3e50"
COLOR_SUBTEXTO = "#7f8c8d"
COLOR_TARJETA  = "#ffffff"
COLOR_ACENTO   = "#00b894"
COLOR_ROJO     = "#e74c3c"
COLOR_AZUL     = "#3498db"
COLOR_FONDO    = "#f0f4f8"


def inventario_view(page: ft.Page):
    hoy = date.today()

    def snack(texto, color=COLOR_ACENTO):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto, color="white"),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    def card(content):
        return ft.Container(
            content=content,
            bgcolor=COLOR_TARJETA,
            border_radius=12,
            padding=18,
            expand=True,
        )

    # ── Filtro de fechas (historial) ────────────────────────
    desde = ft.TextField(label="Desde", value=str(hoy), width=160)
    hasta = ft.TextField(label="Hasta", value=str(hoy), width=160)

    # ── Formulario de nueva entrada ──────────────────────────
    productos_disp = get_productos(include_sin_stock=True)

    dd_producto = ft.Dropdown(
        label="Producto",
        width=260,
        options=[
            ft.dropdown.Option(str(p["id"]), f"{p['nombre']} (stock: {p['stock']})")
            for p in productos_disp
        ],
    )
    campo_cantidad = ft.TextField(
        label="Cantidad", width=140,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    campo_costo_unitario = ft.TextField(
        label="Costo unitario", prefix_text="$", width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    campo_proveedor = ft.TextField(
        label="Proveedor (opcional)", width=220,
    )
    chk_actualizar_costo = ft.Checkbox(
        label="Actualizar el costo de este producto",
        value=True,
    )

    lbl_costo_total = ft.Text(
        "Total a pagar: $0.00", size=14,
        weight=ft.FontWeight.BOLD, color=COLOR_ACENTO,
    )

    def recalcular_total(e=None):
        try:
            cant = float(campo_cantidad.value or 0)
            costo = float(campo_costo_unitario.value or 0)
            lbl_costo_total.value = f"Total a pagar: ${cant * costo:.2f}"
        except ValueError:
            lbl_costo_total.value = "Total a pagar: $0.00"
        page.update()

    campo_cantidad.on_change = recalcular_total
    campo_costo_unitario.on_change = recalcular_total

    # ── Historial ─────────────────────────────────────────
    historial_list = ft.Column(spacing=8)
    stats_row = ft.Row(spacing=12, wrap=True, run_spacing=12)

    def stat_box(icono, label, valor, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icono, size=20),
                    ft.Text(valor, size=18, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(label, size=11, color=COLOR_SUBTEXTO),
                ],
                spacing=2
            ),
            bgcolor=COLOR_FONDO, border_radius=10, padding=14, width=170, height=90,
        )

    def cargar_historial():
        entradas = get_entradas_inventario(desde.value, hasta.value)

        total_invertido = sum(e["costo_total"] for e in entradas)
        total_unidades = sum(e["cantidad"] for e in entradas)

        stats_row.controls = [
            stat_box("📥", "Entradas", str(len(entradas)), COLOR_AZUL),
            stat_box("📦", "Unidades compradas", f"{total_unidades:.0f}", COLOR_TEXTO),
            stat_box("💸", "Total invertido", f"${total_invertido:.2f}", COLOR_ROJO),
        ]

        if entradas:
            historial_list.controls = [
                ft.Container(
                    bgcolor=COLOR_FONDO, border_radius=8, padding=12,
                    content=ft.Row(
                        controls=[
                            ft.Text(e["fecha"], size=12, color=COLOR_SUBTEXTO, width=90),
                            ft.Text(e["producto_nombre"], size=13, color=COLOR_TEXTO,
                                     weight=ft.FontWeight.BOLD, expand=True,
                                     max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"x{e['cantidad']:.0f}", size=12, color=COLOR_SUBTEXTO, width=50),
                            ft.Text(f"${e['costo_unitario']:.2f} c/u", size=12, color=COLOR_SUBTEXTO, width=90),
                            ft.Text(e["proveedor"] or "—", size=12, color=COLOR_SUBTEXTO, width=110,
                                     max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"${e['costo_total']:.2f}", size=13, color=COLOR_ROJO,
                                     weight=ft.FontWeight.BOLD, width=80, text_align=ft.TextAlign.RIGHT),
                        ],
                        spacing=8,
                    ),
                ) for e in entradas
            ]
        else:
            historial_list.controls = [
                ft.Text("Sin entradas de inventario en este rango", color=COLOR_SUBTEXTO, italic=True)
            ]
        page.update()

    def limpiar_formulario():
        dd_producto.value = None
        campo_cantidad.value = ""
        campo_costo_unitario.value = ""
        campo_proveedor.value = ""
        chk_actualizar_costo.value = True
        lbl_costo_total.value = "Total a pagar: $0.00"

    def registrar_entrada(e):
        if not dd_producto.value or not campo_cantidad.value or not campo_costo_unitario.value:
            snack("⚠️ Producto, cantidad y costo unitario son obligatorios", COLOR_ROJO)
            return

        try:
            cantidad = float(campo_cantidad.value)
            costo_unitario = float(campo_costo_unitario.value)
        except ValueError:
            snack("⚠️ Cantidad y costo deben ser números", COLOR_ROJO)
            return

        if cantidad <= 0:
            snack("⚠️ La cantidad debe ser mayor a cero", COLOR_ROJO)
            return

        try:
            crear_entrada_inventario({
                "producto_id": dd_producto.value,
                "cantidad": cantidad,
                "costo_unitario": costo_unitario,
                "proveedor": campo_proveedor.value.strip() or None,
                "fecha": str(hoy),
                "actualizar_costo_producto": chk_actualizar_costo.value,
            })
            limpiar_formulario()
            cargar_historial()
            # Refrescar opciones de producto (el stock mostrado cambió)
            nuevos_productos = get_productos(include_sin_stock=True)
            dd_producto.options = [
                ft.dropdown.Option(str(p["id"]), f"{p['nombre']} (stock: {p['stock']})")
                for p in nuevos_productos
            ]
            snack("✅ Entrada registrada. Stock y gasto actualizados")
        except Exception as ex:
            snack(f"❌ Error: {ex}", COLOR_ROJO)

    formulario_tab = card(
        ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("📥 Registrar Entrada de Inventario", size=18,
                        weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Text(
                    "Al registrar una compra, se actualiza el stock del producto "
                    "y se crea automáticamente un gasto en la categoría Insumos.",
                    size=12, color=COLOR_SUBTEXTO,
                ),
                ft.Divider(),
                ft.Row([dd_producto, campo_cantidad], spacing=12, wrap=True),
                ft.Row([campo_costo_unitario, campo_proveedor], spacing=12, wrap=True),
                chk_actualizar_costo,
                lbl_costo_total,
                ft.ElevatedButton(
                    "➕ Registrar Entrada",
                    height=48,
                    bgcolor=COLOR_ACENTO,
                    color="white",
                    on_click=registrar_entrada,
                ),
            ],
            spacing=12,
        )
    )

    historial_tab = card(
        ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("📜 Historial de Compras", size=18,
                        weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Row(
                    controls=[
                        desde, hasta,
                        ft.ElevatedButton(
                            "🔄 Actualizar", height=48,
                            bgcolor=COLOR_AZUL, color="white",
                            on_click=lambda e: cargar_historial()
                        ),
                    ],
                    spacing=12, wrap=True,
                ),
                stats_row,
                ft.Divider(),
                historial_list,
            ],
            spacing=14,
        )
    )

    cargar_historial()

    return ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Text("📥 Inventario", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Container(
                    expand=True,
                    content=ft.Tabs(
                        selected_index=0,
                        animation_duration=250,
                        expand=True,
                        tabs=[
                            ft.Tab(text="Nueva Entrada", content=formulario_tab),
                            ft.Tab(text="Historial", content=historial_tab),
                        ],
                    ),
                ),
            ],
        ),
    )
# views/ventas_view.py
import flet as ft
from controllers.ventas_controller import obtener_categorias, obtener_productos, Carrito
from database.db_manager import get_clientes

COLOR_ACENTO     = "#ff7a00"
COLOR_EXITO      = "#00b894"
COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#f0f2f5"
COLOR_SECUNDARIO = "#ffffff"
COLOR_PRIMARIO   = "#f5f7fb"


def ventas_view(page: ft.Page):
    carrito = Carrito()
    categorias = obtener_categorias()

    def mostrar_mensaje(texto, color=COLOR_EXITO):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto, color="white"),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    def hacer_tarjeta(prod):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(prod["icono"] or "🍽️", size=24),
                            ft.Text(
                                f"${prod['precio']:.2f}",
                                color=COLOR_ACENTO,
                                weight=ft.FontWeight.BOLD,
                                size=14
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Text(
                        prod["nombre"],
                        color=COLOR_TEXTO,
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        f"Stock: {prod['stock']}",
                        color=COLOR_SUBTEXTO,
                        size=10
                    ),
                    ft.ElevatedButton(
                        "＋ Agregar",
                        bgcolor=COLOR_ACENTO,
                        color="white",
                        on_click=lambda e, p=prod: agregar(p)
                    )
                ],
                spacing=4
            ),
            bgcolor=COLOR_TARJETA,
            border_radius=10,
            padding=10,
            width=175,
            height=165,
        )

    grid = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=200,
        spacing=8,
        run_spacing=8,
    )

    lista     = ft.ListView(expand=True, spacing=4)
    lbl_total = ft.Text("$0.00", size=22,
                        weight=ft.FontWeight.BOLD, color=COLOR_ACENTO)
    lbl_items = ft.Text("0 items", size=11, color=COLOR_SUBTEXTO)

    cliente_seleccionado = {"id": None, "nombre": "Sin cliente"}

    opciones_clientes = [
        ft.dropdown.Option(key="", text="Sin cliente (venta general)")
    ] + [
        ft.dropdown.Option(key=c["id"], text=c["nombre"])
        for c in get_clientes()
    ]

    def cambiar_cliente(e):
        valor = dd_cliente.value
        if valor:
            cliente = next((c for c in get_clientes() if c["id"] == valor), None)
            cliente_seleccionado["id"] = valor
            cliente_seleccionado["nombre"] = cliente["nombre"] if cliente else "Cliente"
        else:
            cliente_seleccionado["id"] = None
            cliente_seleccionado["nombre"] = "Sin cliente"

    dd_cliente = ft.Dropdown(
        label="Cliente",
        hint_text="Sin cliente (venta general)",
        options=opciones_clientes,
        on_change=cambiar_cliente,
        height=48,
    )

    def refrescar_grid(prods):
        grid.controls.clear()
        for p in prods:
            grid.controls.append(hacer_tarjeta(p))
        page.update()

    def refrescar_carrito():
        lista.controls.clear()
        for pid, item in carrito.items.items():
            sub = item["precio"] * item["cantidad"]
            lista.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(item["nombre"], size=12,
                                            color=COLOR_TEXTO, max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(f"${item['precio']:.2f} c/u",
                                            size=10, color=COLOR_SUBTEXTO),
                                ],
                                expand=True,
                                spacing=2
                            ),
                            ft.ElevatedButton(
                                "－",
                                on_click=lambda e, p=pid: quitar(p),
                                bgcolor=COLOR_ACENTO,
                                color="white",
                                width=36,
                                height=32,
                            ),
                            ft.Text(
                                str(item["cantidad"]),
                                size=13,
                                color=COLOR_TEXTO,
                                weight=ft.FontWeight.BOLD,
                                width=24,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.ElevatedButton(
                                "＋",
                                on_click=lambda e, p=dict(pid=pid, **item):
                                    agregar({
                                        "id":     p["pid"],
                                        "nombre": p["nombre"],
                                        "precio": p["precio"],
                                        "stock":  p["stock"]
                                    }),
                                bgcolor=COLOR_EXITO,
                                color="white",
                                width=36,
                                height=32,
                            ),
                            ft.Text(
                                f"${sub:.2f}",
                                size=12,
                                color=COLOR_TEXTO,
                                weight=ft.FontWeight.BOLD,
                                width=52,
                                text_align=ft.TextAlign.RIGHT
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    bgcolor=COLOR_PRIMARIO,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4)
                )
            )
        lbl_total.value = f"${carrito.total():.2f}"
        lbl_items.value = f"{carrito.cantidad_items()} items"
        page.update()

    def agregar(prod):
        ok, msg = carrito.agregar(prod)
        if ok:
            refrescar_carrito()
        else:
            mostrar_mensaje(msg, "#e65100")

    def quitar(pid):
        carrito.quitar(pid)
        refrescar_carrito()

    def vaciar(e):
        carrito.vaciar()
        refrescar_carrito()
        mostrar_mensaje("🗑️ Carrito vaciado")

    def buscar(e):
        txt = campo.value.strip()
        refrescar_grid(obtener_productos(busqueda=txt if txt else None))

    def filtrar(e, cid):
        refrescar_grid(obtener_productos(categoria_id=cid))

    def todos(e):
        campo.value = ""
        refrescar_grid(obtener_productos())

    campo = ft.TextField(
        hint_text="🔍 Buscar...",
        on_change=buscar,
        bgcolor=COLOR_TARJETA,
        color=COLOR_TEXTO,
        border_radius=8,
        height=42,
        expand=True
    )

    categorias_row = ft.Row(
        controls=[ft.TextButton("Todos", on_click=todos)] + [
            ft.TextButton(
                f"{c['icono']} {c['nombre']}",
                on_click=lambda e, cid=c["id"]: filtrar(e, cid)
            )
            for c in categorias
        ],
        scroll=ft.ScrollMode.AUTO
    )

    def cobrar(e):
        if carrito.esta_vacio():
            mostrar_mensaje("⚠️ Carrito vacío", "#e65100")
            return
        from views.cobro_view import cobro_view
        area = page.controls[0].controls[1]
        area.content = cobro_view(
            page, carrito,
            cliente_id=cliente_seleccionado["id"],
            cliente_nombre=cliente_seleccionado["nombre"],
            on_venta_completada=lambda: recargar_ventas()
        )
        page.update()

    def recargar_ventas():
        area = page.controls[0].controls[1]
        area.content = ventas_view(page)
        page.update()

    btn_cobrar = ft.ElevatedButton(
        "🛒  COBRAR",
        color="white",
        bgcolor=COLOR_EXITO,
        on_click=cobrar,
        height=52,
        expand=True,
    )

    refrescar_grid(obtener_productos())

    izquierda = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("🍽️ Catálogo", size=18,
                        weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Row(controls=[campo]),
                categorias_row,
                ft.Divider(height=1),
                grid,
            ],
            spacing=8,
            expand=True
        ),
        expand=3,
        bgcolor=COLOR_SECUNDARIO,
        border_radius=14,
        padding=14
    )

    derecha = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("🛒 Orden", size=18,
                                weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                        lbl_items
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                dd_cliente,
                lista,
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Text("TOTAL", size=15, color=COLOR_SUBTEXTO),
                        lbl_total
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.TextButton("🗑️ Vaciar", on_click=vaciar),
                btn_cobrar,
            ],
            spacing=8,
            expand=True
        ),
        expand=2,
        bgcolor=COLOR_SECUNDARIO,
        border_radius=14,
        padding=14
    )

    return ft.Row(
        controls=[izquierda, derecha],
        expand=True,
        spacing=14
    )
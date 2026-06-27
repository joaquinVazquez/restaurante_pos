# views/clientes_view.py
import flet as ft
from database.db_manager import (
    get_clientes, crear_cliente, actualizar_cliente,
    desactivar_cliente, get_historial_cliente
)

COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#ffffff"
COLOR_ACENTO     = "#00b894"
COLOR_ROJO       = "#e74c3c"
COLOR_AZUL       = "#3498db"
COLOR_NARANJA    = "#ff7a00"
COLOR_FONDO      = "#f0f4f8"


def clientes_view(page: ft.Page):

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Cliente", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Compras", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total Gastado", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.Border(ft.BorderSide(1, "#e0e0e0"), ft.BorderSide(1, "#e0e0e0"), ft.BorderSide(1, "#e0e0e0"), ft.BorderSide(1, "#e0e0e0")),
        border_radius=10,
        heading_row_color="#f8f9fa",
        heading_row_height=44,
        data_row_min_height=52,
        expand=True,
    )

    def refrescar_tabla(busqueda=""):
        clientes = get_clientes(busqueda)
        tabla.rows.clear()
        for c in clientes:
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(
                        ft.Column(
                            controls=[
                                ft.Text(c["nombre"], size=13,
                                        color=COLOR_TEXTO,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(c.get("notas") or "",
                                        size=11,
                                        color=COLOR_SUBTEXTO,
                                        italic=True),
                            ],
                            spacing=2
                        )
                    ),
                    ft.DataCell(ft.Text(
                        c.get("telefono") or "—",
                        size=13, color=COLOR_TEXTO
                    )),
                    ft.DataCell(ft.Text(
                        c.get("email") or "—",
                        size=12, color=COLOR_SUBTEXTO
                    )),
                    ft.DataCell(ft.Container(
                        content=ft.Text(
                            str(c.get("total_compras", 0)),
                            size=11, color="white",
                            weight=ft.FontWeight.BOLD
                        ),
                        bgcolor=COLOR_ACENTO,
                        border_radius=20,
                        padding=ft.Padding(10, 4, 10, 4)
                    )),
                    ft.DataCell(ft.Text(
                        f"${c.get('total_gastado', 0):.2f}",
                        size=13, color=COLOR_AZUL,
                        weight=ft.FontWeight.BOLD
                    )),
                    ft.DataCell(
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    "📋 Historial",
                                    on_click=lambda e, cli=c:
                                        ver_historial(cli)
                                ),
                                ft.TextButton(
                                    "✏️ Editar",
                                    on_click=lambda e, cli=c:
                                        abrir_editar(cli)
                                ),
                                ft.TextButton(
                                    "🗑️",
                                    on_click=lambda e, cli=c:
                                        confirmar_eliminar(cli),
                                    style=ft.ButtonStyle(
                                        color=COLOR_ROJO)
                                ),
                            ],
                            spacing=0
                        )
                    ),
                ])
            )
        page.update()

    campo_nombre    = ft.TextField(label="Nombre completo *",
                                   border_radius=8, expand=True)
    campo_telefono  = ft.TextField(label="Teléfono",
                                   border_radius=8, expand=True,
                                   keyboard_type=ft.KeyboardType.PHONE)
    campo_email     = ft.TextField(label="Email",
                                   border_radius=8, expand=True,
                                   keyboard_type=ft.KeyboardType.EMAIL)
    campo_direccion = ft.TextField(label="Dirección",
                                   border_radius=8, expand=True)
    campo_notas     = ft.TextField(label="Notas",
                                   border_radius=8, expand=True,
                                   multiline=True, min_lines=2,
                                   max_lines=3)
    titulo_dialogo  = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
    cliente_editando = {"id": None}

    dialogo = ft.AlertDialog(
        modal=True,
        title=titulo_dialogo,
        content=ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(controls=[campo_nombre]),
                    ft.Row(
                        controls=[campo_telefono, campo_email],
                        spacing=12
                    ),
                    ft.Row(controls=[campo_direccion]),
                    ft.Row(controls=[campo_notas]),
                ],
                spacing=12, tight=True
            ),
            width=460, height=320, padding=10
        ),
        actions=[
            ft.TextButton("Cancelar",
                          on_click=lambda e: cerrar_dialogo()),
            ft.ElevatedButton(
                "Guardar",
                bgcolor=COLOR_ACENTO, color="white",
                on_click=lambda e: guardar_cliente()
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def abrir_agregar(e):
        titulo_dialogo.value    = "➕ Agregar Cliente"
        cliente_editando["id"]  = None
        campo_nombre.value      = ""
        campo_telefono.value    = ""
        campo_email.value       = ""
        campo_direccion.value   = ""
        campo_notas.value       = ""
        if dialogo not in page.overlay:
            page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def abrir_editar(cli):
        titulo_dialogo.value    = "✏️ Editar Cliente"
        cliente_editando["id"]  = cli["id"]
        campo_nombre.value      = cli["nombre"]
        campo_telefono.value    = cli.get("telefono") or ""
        campo_email.value       = cli.get("email") or ""
        campo_direccion.value   = cli.get("direccion") or ""
        campo_notas.value       = cli.get("notas") or ""
        if dialogo not in page.overlay:
            page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def cerrar_dialogo():
        dialogo.open = False
        page.update()

    def guardar_cliente():
        nombre = campo_nombre.value.strip()
        if not nombre:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("⚠️ El nombre es obligatorio",
                                color="white"),
                bgcolor=COLOR_NARANJA
            )
            page.snack_bar.open = True
            page.update()
            return

        datos = {
            "nombre":    nombre,
            "telefono":  campo_telefono.value.strip() or None,
            "email":     campo_email.value.strip() or None,
            "direccion": campo_direccion.value.strip() or None,
            "notas":     campo_notas.value.strip() or None,
        }

        if cliente_editando["id"]:
            actualizar_cliente(cliente_editando["id"], datos)
            msg = "✅ Cliente actualizado"
        else:
            crear_cliente(datos)
            msg = "✅ Cliente agregado"

        cerrar_dialogo()
        refrescar_tabla()
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=COLOR_ACENTO
        )
        page.snack_bar.open = True
        page.update()

    dialogo_eliminar = ft.AlertDialog(
        modal=True,
        title=ft.Text("🗑️ Eliminar Cliente"),
        content=ft.Text(
            "¿Estás seguro? El cliente será desactivado."),
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
    cliente_a_eliminar = {"id": None}

    def confirmar_eliminar(cli):
        cliente_a_eliminar["id"] = cli["id"]
        if dialogo_eliminar not in page.overlay:
            page.overlay.append(dialogo_eliminar)
        dialogo_eliminar.open = True
        page.update()

    def cerrar_eliminar():
        dialogo_eliminar.open = False
        page.update()

    def ejecutar_eliminar():
        desactivar_cliente(cliente_a_eliminar["id"])
        cerrar_eliminar()
        refrescar_tabla()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("🗑️ Cliente eliminado", color="white"),
            bgcolor=COLOR_ROJO
        )
        page.snack_bar.open = True
        page.update()

    tabla_historial = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("# Venta", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Productos", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Pago", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.Border(ft.BorderSide(1, "#e0e0e0"), ft.BorderSide(1, "#e0e0e0"), ft.BorderSide(1, "#e0e0e0"), ft.BorderSide(1, "#e0e0e0")),
        border_radius=10,
        heading_row_color="#f8f9fa",
        heading_row_height=44,
        data_row_min_height=44,
    )

    nombre_cliente_historial = ft.Text(
        "", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO
    )

    dialogo_historial = ft.AlertDialog(
        modal=True,
        title=ft.Text("📋 Historial de Compras",
                      size=16, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    nombre_cliente_historial,
                    ft.Divider(),
                    ft.Container(
                        content=ft.ListView(
                            controls=[tabla_historial],
                            expand=True
                        ),
                        height=300, expand=True
                    )
                ],
                spacing=8, tight=True
            ),
            width=600, padding=10
        ),
        actions=[
            ft.TextButton("Cerrar",
                          on_click=lambda e: cerrar_historial()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def cerrar_historial():
        dialogo_historial.open = False
        page.update()

    def ver_historial(cli):
        nombre_cliente_historial.value = (
            f"Cliente: {cli['nombre']} — "
            f"{cli.get('total_compras', 0)} compras — "
            f"${cli.get('total_gastado', 0):.2f} total"
        )
        historial = get_historial_cliente(cli["id"])
        tabla_historial.rows.clear()

        if not historial:
            tabla_historial.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Sin compras registradas",
                                        color=COLOR_SUBTEXTO,
                                        italic=True)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        else:
            for v in historial:
                tabla_historial.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(
                            f"#{str(v['id'])[:8]}", size=13,
                            color=COLOR_TEXTO,
                            weight=ft.FontWeight.BOLD
                        )),
                        ft.DataCell(ft.Text(
                            str(v.get("creado_en", "")),
                            size=12, color=COLOR_SUBTEXTO
                        )),
                        ft.DataCell(ft.Text(
                            str(v.get("productos", 0)),
                            size=13, color=COLOR_TEXTO
                        )),
                        ft.DataCell(ft.Text(
                            f"${v.get('total', 0):.2f}",
                            size=13, color=COLOR_ACENTO,
                            weight=ft.FontWeight.BOLD
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                "💵" if v.get("metodo_pago") == "efectivo"
                                else "💳",
                                size=14
                            ),
                            bgcolor=COLOR_ACENTO
                            if v.get("metodo_pago") == "efectivo"
                            else COLOR_AZUL,
                            border_radius=20,
                            padding=ft.Padding(10, 4, 10, 4)
                        )),
                    ])
                )

        if dialogo_historial not in page.overlay:
            page.overlay.append(dialogo_historial)
        dialogo_historial.open = True
        page.update()

    campo_busqueda = ft.TextField(
        hint_text="🔍 Buscar por nombre, teléfono o email...",
        on_change=lambda e: refrescar_tabla(e.control.value),
        border_radius=8, height=42, expand=True, bgcolor="white"
    )

    refrescar_tabla()

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("👥 Clientes", size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_TEXTO),
                            ft.Text("Gestiona tu base de clientes",
                                    size=13, color=COLOR_SUBTEXTO),
                        ],
                        spacing=2
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "➕ Agregar Cliente",
                        bgcolor=COLOR_ACENTO, color="white",
                        height=42, on_click=abrir_agregar
                    ),
                ]
            ),
            ft.Container(height=8),
            ft.Row(controls=[campo_busqueda]),
            ft.Container(height=8),
            ft.Container(
                content=ft.ListView(
                    controls=[tabla], expand=True
                ),
                bgcolor=COLOR_TARJETA,
                border_radius=12, padding=8, expand=True,
                shadow=ft.BoxShadow(
                    blur_radius=8, color="#00000010",
                    offset=ft.Offset(0, 2)
                )
            )
        ],
        expand=True,
        spacing=0
    )




# views/clientes_view.py
import flet as ft
from database.connection import execute_query

COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#ffffff"
COLOR_ACENTO     = "#00b894"
COLOR_ROJO       = "#e74c3c"
COLOR_AZUL       = "#3498db"
COLOR_NARANJA    = "#ff7a00"
COLOR_FONDO      = "#f0f4f8"


def clientes_view(page: ft.Page):

    # ── Consultas ──────────────────────────────────────────
    def get_clientes(busqueda=""):
        return execute_query("""
            SELECT c.id, c.nombre, c.telefono, c.email,
                   c.direccion, c.notas, c.activo,
                   COUNT(v.id)              AS total_compras,
                   COALESCE(SUM(v.total),0) AS total_gastado
            FROM clientes c
            LEFT JOIN ventas v ON v.cliente_id = c.id
            WHERE c.activo = TRUE
              AND (LOWER(c.nombre)   LIKE LOWER(%s)
                OR LOWER(c.telefono) LIKE LOWER(%s)
                OR LOWER(c.email)    LIKE LOWER(%s))
            GROUP BY c.id, c.nombre, c.telefono,
                     c.email, c.direccion, c.notas, c.activo
            ORDER BY c.nombre
        """, [f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"])

    def get_historial(cliente_id):
        return execute_query("""
            SELECT v.id, v.total, v.metodo_pago, v.creado_en,
                   COUNT(dv.id) AS productos
            FROM ventas v
            LEFT JOIN detalle_ventas dv ON dv.venta_id = v.id
            WHERE v.cliente_id = %s
            GROUP BY v.id, v.total, v.metodo_pago, v.creado_en
            ORDER BY v.creado_en DESC
        """, [cliente_id])

    # ── Tabla principal ────────────────────────────────────
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Cliente",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Teléfono",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Email",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Compras",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total Gastado",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Acciones",
                                  weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, "#e0e0e0"),
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
                                ft.Text(c["notas"] or "",
                                        size=11,
                                        color=COLOR_SUBTEXTO,
                                        italic=True),
                            ],
                            spacing=2
                        )
                    ),
                    ft.DataCell(ft.Text(
                        c["telefono"] or "—",
                        size=13, color=COLOR_TEXTO
                    )),
                    ft.DataCell(ft.Text(
                        c["email"] or "—",
                        size=12, color=COLOR_SUBTEXTO
                    )),
                    ft.DataCell(ft.Container(
                        content=ft.Text(
                            str(c["total_compras"]),
                            size=11, color="white",
                            weight=ft.FontWeight.BOLD
                        ),
                        bgcolor=COLOR_ACENTO,
                        border_radius=20,
                        padding=ft.padding.symmetric(
                            horizontal=10, vertical=4)
                    )),
                    ft.DataCell(ft.Text(
                        f"${c['total_gastado']:.2f}",
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

    # ── Campos formulario ──────────────────────────────────
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
    titulo_dialogo  = ft.Text("", size=18,
                               weight=ft.FontWeight.BOLD)
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
                spacing=12,
                tight=True
            ),
            width=460,
            height=320,
            padding=10
        ),
        actions=[
            ft.TextButton("Cancelar",
                          on_click=lambda e: cerrar_dialogo()),
            ft.ElevatedButton(
                "Guardar",
                bgcolor=COLOR_ACENTO,
                color="white",
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
        campo_telefono.value    = cli["telefono"] or ""
        campo_email.value       = cli["email"] or ""
        campo_direccion.value   = cli["direccion"] or ""
        campo_notas.value       = cli["notas"] or ""
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

        if cliente_editando["id"]:
            execute_query("""
                UPDATE clientes
                SET nombre=%s, telefono=%s, email=%s,
                    direccion=%s, notas=%s
                WHERE id=%s
            """, [
                nombre,
                campo_telefono.value.strip() or None,
                campo_email.value.strip() or None,
                campo_direccion.value.strip() or None,
                campo_notas.value.strip() or None,
                cliente_editando["id"]
            ], fetch=False)
            msg = "✅ Cliente actualizado"
        else:
            execute_query("""
                INSERT INTO clientes
                    (nombre, telefono, email, direccion, notas)
                VALUES (%s, %s, %s, %s, %s)
            """, [
                nombre,
                campo_telefono.value.strip() or None,
                campo_email.value.strip() or None,
                campo_direccion.value.strip() or None,
                campo_notas.value.strip() or None,
            ], fetch=False)
            msg = "✅ Cliente agregado"

        cerrar_dialogo()
        refrescar_tabla()
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=COLOR_ACENTO
        )
        page.snack_bar.open = True
        page.update()

    # ── Eliminar ───────────────────────────────────────────
    cliente_a_eliminar = {"id": None}
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
        execute_query(
            "UPDATE clientes SET activo=FALSE WHERE id=%s",
            [cliente_a_eliminar["id"]], fetch=False
        )
        cerrar_eliminar()
        refrescar_tabla()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("🗑️ Cliente eliminado", color="white"),
            bgcolor=COLOR_ROJO
        )
        page.snack_bar.open = True
        page.update()

    # ── Historial de compras ───────────────────────────────
    tabla_historial = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("# Venta",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Productos",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Pago",
                                  weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, "#e0e0e0"),
        border_radius=10,
        heading_row_color="#f8f9fa",
        heading_row_height=44,
        data_row_min_height=44,
    )

    nombre_cliente_historial = ft.Text(
        "", size=16, weight=ft.FontWeight.BOLD,
        color=COLOR_TEXTO
    )

    dialogo_historial = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Text("📋 Historial de Compras",
                        size=16, weight=ft.FontWeight.BOLD),
            ]
        ),
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
                        height=300,
                        expand=True
                    )
                ],
                spacing=8,
                tight=True
            ),
            width=600,
            padding=10
        ),
        actions=[
            ft.TextButton(
                "Cerrar",
                on_click=lambda e: cerrar_historial()
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def cerrar_historial():
        dialogo_historial.open = False
        page.update()

    def ver_historial(cli):
        nombre_cliente_historial.value = (
            f"Cliente: {cli['nombre']} — "
            f"{cli['total_compras']} compras — "
            f"${cli['total_gastado']:.2f} total"
        )
        historial = get_historial(cli["id"])
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
                            f"#{v['id']}", size=13,
                            color=COLOR_TEXTO,
                            weight=ft.FontWeight.BOLD
                        )),
                        ft.DataCell(ft.Text(
                            v["creado_en"].strftime("%d/%m/%Y %H:%M"),
                            size=12, color=COLOR_SUBTEXTO
                        )),
                        ft.DataCell(ft.Text(
                            str(v["productos"]),
                            size=13, color=COLOR_TEXTO
                        )),
                        ft.DataCell(ft.Text(
                            f"${v['total']:.2f}",
                            size=13, color=COLOR_ACENTO,
                            weight=ft.FontWeight.BOLD
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                "💵" if v["metodo_pago"] == "efectivo"
                                else "💳",
                                size=14
                            ),
                            bgcolor=COLOR_ACENTO
                            if v["metodo_pago"] == "efectivo"
                            else COLOR_AZUL,
                            border_radius=20,
                            padding=ft.padding.symmetric(
                                horizontal=10, vertical=4)
                        )),
                    ])
                )

        if dialogo_historial not in page.overlay:
            page.overlay.append(dialogo_historial)
        dialogo_historial.open = True
        page.update()

    # ── Búsqueda ───────────────────────────────────────────
    campo_busqueda = ft.TextField(
        hint_text="🔍 Buscar por nombre, teléfono o email...",
        on_change=lambda e: refrescar_tabla(e.control.value),
        border_radius=8,
        height=42,
        expand=True,
        bgcolor="white"
    )

    refrescar_tabla()

    # ── Layout ─────────────────────────────────────────────
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
                        bgcolor=COLOR_ACENTO,
                        color="white",
                        height=42,
                        on_click=abrir_agregar
                    ),
                ]
            ),
            ft.Container(height=8),
            ft.Row(controls=[campo_busqueda]),
            ft.Container(height=8),
            ft.Container(
                content=ft.ListView(
                    controls=[tabla],
                    expand=True
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
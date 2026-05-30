# views/reportes_view.py
import flet as ft
from datetime import datetime, date, timedelta
from database.connection import execute_query
import os

COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#ffffff"
COLOR_ACENTO     = "#00b894"
COLOR_ROJO       = "#e74c3c"
COLOR_AZUL       = "#3498db"
COLOR_NARANJA    = "#ff7a00"
COLOR_FONDO      = "#f0f4f8"
COLOR_MORADO     = "#9b59b6"


def reportes_view(page: ft.Page):

    # ── Filtros de fecha ───────────────────────────────────
    filtro_actual = {"desde": None, "hasta": None, "periodo": "hoy"}

    def get_rango(periodo):
        hoy = date.today()
        if periodo == "hoy":
            return hoy, hoy
        elif periodo == "semana":
            return hoy - timedelta(days=7), hoy
        elif periodo == "mes":
            return hoy.replace(day=1), hoy
        elif periodo == "año":
            return hoy.replace(month=1, day=1), hoy
        return hoy, hoy

    # ── Consultas ──────────────────────────────────────────
    def get_resumen(desde, hasta):
        return execute_query("""
            SELECT
                COUNT(*)                    AS total_ventas,
                COALESCE(SUM(total), 0)     AS ingresos,
                COALESCE(AVG(total), 0)     AS ticket_promedio,
                COALESCE(MAX(total), 0)     AS venta_mayor
            FROM ventas
            WHERE DATE(creado_en) BETWEEN %s AND %s
        """, [desde, hasta])

    def get_ventas_por_dia(desde, hasta):
        return execute_query("""
            SELECT
                DATE(creado_en)             AS fecha,
                COUNT(*)                    AS cantidad,
                COALESCE(SUM(total), 0)     AS total
            FROM ventas
            WHERE DATE(creado_en) BETWEEN %s AND %s
            GROUP BY DATE(creado_en)
            ORDER BY fecha DESC
        """, [desde, hasta])

    def get_productos_top(desde, hasta):
        return execute_query("""
            SELECT
                p.nombre,
                SUM(dv.cantidad)            AS vendidos,
                SUM(dv.subtotal)            AS ingresos
            FROM detalle_ventas dv
            JOIN productos p ON dv.producto_id = p.id
            JOIN ventas v ON dv.venta_id = v.id
            WHERE DATE(v.creado_en) BETWEEN %s AND %s
            GROUP BY p.nombre
            ORDER BY vendidos DESC
            LIMIT 10
        """, [desde, hasta])

    def get_historial_ventas(desde, hasta):
        return execute_query("""
            SELECT
                v.id,
                v.total,
                v.metodo_pago,
                v.creado_en,
                COUNT(dv.id)                AS productos
            FROM ventas v
            LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
            WHERE DATE(v.creado_en) BETWEEN %s AND %s
            GROUP BY v.id, v.total, v.metodo_pago, v.creado_en
            ORDER BY v.creado_en DESC
        """, [desde, hasta])

    # ── Componentes UI ─────────────────────────────────────
    lbl_total_ventas  = ft.Text("0", size=28, weight=ft.FontWeight.BOLD,
                                color=COLOR_ACENTO)
    lbl_ingresos      = ft.Text("$0.00", size=28, weight=ft.FontWeight.BOLD,
                                color=COLOR_AZUL)
    lbl_promedio      = ft.Text("$0.00", size=28, weight=ft.FontWeight.BOLD,
                                color=COLOR_NARANJA)
    lbl_mayor         = ft.Text("$0.00", size=28, weight=ft.FontWeight.BOLD,
                                color=COLOR_MORADO)
    lbl_periodo       = ft.Text("Hoy", size=13, color=COLOR_SUBTEXTO)

    tabla_dias = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ventas", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Promedio", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, "#e0e0e0"),
        border_radius=10,
        heading_row_color="#f8f9fa",
        heading_row_height=44,
        data_row_min_height=44,
    )

    tabla_productos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Vendidos", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ingresos", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, "#e0e0e0"),
        border_radius=10,
        heading_row_color="#f8f9fa",
        heading_row_height=44,
        data_row_min_height=44,
    )

    tabla_historial = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("# Venta", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Hora", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Productos", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Pago", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ticket", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, "#e0e0e0"),
        border_radius=10,
        heading_row_color="#f8f9fa",
        heading_row_height=44,
        data_row_min_height=44,
    )

    # ── Refrescar datos ────────────────────────────────────
    def refrescar(desde, hasta):
        # Resumen
        resumen = get_resumen(desde, hasta)
        if resumen:
            r = resumen[0]
            lbl_total_ventas.value = str(r["total_ventas"])
            lbl_ingresos.value     = f"${r['ingresos']:.2f}"
            lbl_promedio.value     = f"${r['ticket_promedio']:.2f}"
            lbl_mayor.value        = f"${r['venta_mayor']:.2f}"

        # Ventas por día
        tabla_dias.rows.clear()
        for v in get_ventas_por_dia(desde, hasta):
            promedio = v["total"] / v["cantidad"] if v["cantidad"] > 0 else 0
            tabla_dias.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(
                        v["fecha"].strftime("%d/%m/%Y"),
                        size=13, color=COLOR_TEXTO
                    )),
                    ft.DataCell(ft.Text(
                        str(v["cantidad"]),
                        size=13, color=COLOR_TEXTO
                    )),
                    ft.DataCell(ft.Text(
                        f"${v['total']:.2f}",
                        size=13, color=COLOR_ACENTO,
                        weight=ft.FontWeight.BOLD
                    )),
                    ft.DataCell(ft.Text(
                        f"${promedio:.2f}",
                        size=13, color=COLOR_SUBTEXTO
                    )),
                ])
            )

        # Top productos
        tabla_productos.rows.clear()
        for i, p in enumerate(get_productos_top(desde, hasta), 1):
            medalla = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
            tabla_productos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(medalla, size=14)),
                    ft.DataCell(ft.Text(
                        p["nombre"], size=13,
                        color=COLOR_TEXTO,
                        weight=ft.FontWeight.W_500
                    )),
                    ft.DataCell(ft.Container(
                        content=ft.Text(
                            str(p["vendidos"]),
                            size=11, color="white",
                            weight=ft.FontWeight.BOLD
                        ),
                        bgcolor=COLOR_ACENTO,
                        border_radius=20,
                        padding=ft.padding.symmetric(
                            horizontal=10, vertical=4)
                    )),
                    ft.DataCell(ft.Text(
                        f"${p['ingresos']:.2f}",
                        size=13, color=COLOR_AZUL,
                        weight=ft.FontWeight.BOLD
                    )),
                ])
            )

        # Historial completo
        tabla_historial.rows.clear()
        for v in get_historial_ventas(desde, hasta):
            fecha = v["creado_en"]
            ruta_ticket = f"tickets/ticket_{v['id']}.pdf"
            tiene_ticket = os.path.exists(ruta_ticket)

            tabla_historial.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(
                        f"#{v['id']}",
                        size=13, color=COLOR_TEXTO,
                        weight=ft.FontWeight.BOLD
                    )),
                    ft.DataCell(ft.Text(
                        fecha.strftime("%d/%m/%Y"),
                        size=13, color=COLOR_TEXTO
                    )),
                    ft.DataCell(ft.Text(
                        fecha.strftime("%H:%M"),
                        size=13, color=COLOR_SUBTEXTO
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
                            "💵 Efectivo" if v["metodo_pago"] == "efectivo"
                            else "💳 Tarjeta",
                            size=11, color="white"
                        ),
                        bgcolor=COLOR_ACENTO if v["metodo_pago"] == "efectivo"
                        else COLOR_AZUL,
                        border_radius=20,
                        padding=ft.padding.symmetric(
                            horizontal=8, vertical=4)
                    )),
                    ft.DataCell(
                        ft.TextButton(
                            "📄 Ver",
                            on_click=lambda e, r=ruta_ticket: abrir_ticket(r)
                        ) if tiene_ticket else ft.Text(
                            "—", color=COLOR_SUBTEXTO, size=12)
                    ),
                ])
            )

        page.update()

    def abrir_ticket(ruta):
        import subprocess
        subprocess.Popen(
            ["start", "", os.path.abspath(ruta)],
            shell=True
        )

    # ── Exportar reporte PDF ───────────────────────────────
    def exportar_pdf(e):
        try:
            from fpdf import FPDF
            desde = filtro_actual["desde"]
            hasta = filtro_actual["hasta"]
            resumen = get_resumen(desde, hasta)
            productos = get_productos_top(desde, hasta)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(15, 15, 15)

            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "RestaurantePOS — Reporte de Ventas",
                     ln=True, align="C")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6,
                     f"Período: {desde.strftime('%d/%m/%Y')} al {hasta.strftime('%d/%m/%Y')}",
                     ln=True, align="C")
            pdf.cell(0, 6,
                     f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                     ln=True, align="C")
            pdf.ln(6)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(6)

            if resumen:
                r = resumen[0]
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, "Resumen", ln=True)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(95, 7, f"Total de ventas: {r['total_ventas']}")
                pdf.cell(95, 7, f"Ingresos totales: ${r['ingresos']:.2f}",
                         ln=True)
                pdf.cell(95, 7,
                         f"Ticket promedio: ${r['ticket_promedio']:.2f}")
                pdf.cell(95, 7, f"Venta mayor: ${r['venta_mayor']:.2f}",
                         ln=True)
                pdf.ln(4)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Top Productos", ln=True)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(10, 7, "#")
            pdf.cell(100, 7, "Producto")
            pdf.cell(40, 7, "Vendidos", align="C")
            pdf.cell(40, 7, "Ingresos", align="R")
            pdf.ln()
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2)

            pdf.set_font("Helvetica", "", 10)
            for i, p in enumerate(productos, 1):
                pdf.cell(10, 7, str(i))
                pdf.cell(100, 7, p["nombre"][:40])
                pdf.cell(40, 7, str(p["vendidos"]), align="C")
                pdf.cell(40, 7, f"${p['ingresos']:.2f}", align="R")
                pdf.ln()

            os.makedirs("reportes", exist_ok=True)
            nombre = f"reportes/reporte_{desde}_{hasta}.pdf"
            pdf.output(nombre)

            import subprocess
            subprocess.Popen(
                ["start", "", os.path.abspath(nombre)],
                shell=True
            )

            page.snack_bar = ft.SnackBar(
                content=ft.Text("📊 Reporte exportado", color="white"),
                bgcolor=COLOR_ACENTO
            )
            page.snack_bar.open = True
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Error: {ex}", color="white"),
                bgcolor=COLOR_ROJO
            )
            page.snack_bar.open = True
            page.update()

    # ── Botones de periodo ─────────────────────────────────
    def aplicar_periodo(periodo, label):
        filtro_actual["periodo"] = periodo
        desde, hasta = get_rango(periodo)
        filtro_actual["desde"] = desde
        filtro_actual["hasta"] = hasta
        lbl_periodo.value = label
        refrescar(desde, hasta)

        for btn in btns_periodo:
            btn.bgcolor = COLOR_ACENTO if btn.data == periodo else "#e0e0e0"
            btn.color   = "white" if btn.data == periodo else COLOR_TEXTO
        page.update()

    btns_periodo = [
        ft.ElevatedButton(
            "Hoy", data="hoy",
            bgcolor=COLOR_ACENTO, color="white", height=36,
            on_click=lambda e: aplicar_periodo("hoy", "Hoy")
        ),
        ft.ElevatedButton(
            "7 días", data="semana",
            bgcolor="#e0e0e0", color=COLOR_TEXTO, height=36,
            on_click=lambda e: aplicar_periodo("semana", "Últimos 7 días")
        ),
        ft.ElevatedButton(
            "Este mes", data="mes",
            bgcolor="#e0e0e0", color=COLOR_TEXTO, height=36,
            on_click=lambda e: aplicar_periodo("mes", "Este mes")
        ),
        ft.ElevatedButton(
            "Este año", data="año",
            bgcolor="#e0e0e0", color=COLOR_TEXTO, height=36,
            on_click=lambda e: aplicar_periodo("año", "Este año")
        ),
    ]

    # ── Tarjetas de resumen ────────────────────────────────
    def tarjeta(icono, titulo, lbl_valor, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icono, size=26),
                    lbl_valor,
                    ft.Text(titulo, size=12,
                            color=COLOR_SUBTEXTO),
                ],
                spacing=4
            ),
            bgcolor=COLOR_TARJETA,
            border_radius=14,
            padding=16,
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=8,
                color="#00000010",
                offset=ft.Offset(0, 2)
            )
        )

    # ── Cargar datos iniciales ─────────────────────────────
    desde_ini, hasta_ini = get_rango("hoy")
    filtro_actual["desde"] = desde_ini
    filtro_actual["hasta"] = hasta_ini
    refrescar(desde_ini, hasta_ini)

    # ── Layout ─────────────────────────────────────────────
    return ft.Column(
        controls=[
            # Header
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("📊 Reportes", size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_TEXTO),
                            lbl_periodo,
                        ],
                        spacing=2
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "📄 Exportar PDF",
                        bgcolor=COLOR_AZUL,
                        color="white",
                        height=40,
                        on_click=exportar_pdf
                    )
                ]
            ),
            ft.Container(height=4),
            # Filtros
            ft.Row(controls=btns_periodo, spacing=8),
            ft.Container(height=8),
            # Tarjetas resumen
            ft.Row(
                controls=[
                    tarjeta("💰", "Ingresos Totales",
                            lbl_ingresos, COLOR_AZUL),
                    tarjeta("🧾", "Total Ventas",
                            lbl_total_ventas, COLOR_ACENTO),
                    tarjeta("📈", "Ticket Promedio",
                            lbl_promedio, COLOR_NARANJA),
                    tarjeta("⭐", "Venta Mayor",
                            lbl_mayor, COLOR_MORADO),
                ],
                spacing=12
            ),
            ft.Container(height=8),
            # Contenido principal con scroll
            ft.Container(
                content=ft.ListView(
                    controls=[
                        # Ventas por día
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("📅 Ventas por Día", size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_TEXTO),
                                    ft.Divider(),
                                    tabla_dias,
                                ],
                                spacing=8
                            ),
                            bgcolor=COLOR_TARJETA,
                            border_radius=14,
                            padding=16,
                            shadow=ft.BoxShadow(
                                blur_radius=8,
                                color="#00000010",
                                offset=ft.Offset(0, 2)
                            )
                        ),
                        ft.Container(height=12),
                        # Top productos
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("🏆 Productos Más Vendidos",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_TEXTO),
                                    ft.Divider(),
                                    tabla_productos,
                                ],
                                spacing=8
                            ),
                            bgcolor=COLOR_TARJETA,
                            border_radius=14,
                            padding=16,
                            shadow=ft.BoxShadow(
                                blur_radius=8,
                                color="#00000010",
                                offset=ft.Offset(0, 2)
                            )
                        ),
                        ft.Container(height=12),
                        # Historial completo
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("🕐 Historial de Ventas",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_TEXTO),
                                    ft.Divider(),
                                    ft.Container(
                                        content=ft.ListView(
                                            controls=[tabla_historial],
                                            expand=True
                                        ),
                                        expand=True
                                    ),
                                ],
                                spacing=8
                            ),
                            bgcolor=COLOR_TARJETA,
                            border_radius=14,
                            padding=16,
                            shadow=ft.BoxShadow(
                                blur_radius=8,
                                color="#00000010",
                                offset=ft.Offset(0, 2)
                            )
                        ),
                    ],
                    expand=True,
                    spacing=0
                ),
                expand=True
            )
        ],
        expand=True,
        spacing=0
    )
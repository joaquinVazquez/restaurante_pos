# views/caja_view.py
import flet as ft
import os
from datetime import datetime, date
from database.connection import execute_query

COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#ffffff"
COLOR_ACENTO     = "#00b894"
COLOR_ROJO       = "#e74c3c"
COLOR_AZUL       = "#3498db"
COLOR_NARANJA    = "#ff7a00"
COLOR_FONDO      = "#f0f4f8"
COLOR_MORADO     = "#9b59b6"


def caja_view(page: ft.Page):

    # ── Consultas ──────────────────────────────────────────
    def get_caja_hoy():
        return execute_query("""
            SELECT
                COUNT(*)                        AS total_ventas,
                COALESCE(SUM(total), 0)         AS total_ingresos,
                COALESCE(SUM(CASE WHEN metodo_pago='efectivo'
                    THEN total ELSE 0 END), 0)  AS efectivo,
                COALESCE(SUM(CASE WHEN metodo_pago='tarjeta'
                    THEN total ELSE 0 END), 0)  AS tarjeta
            FROM ventas
            WHERE DATE(creado_en) = CURRENT_DATE
        """)

    def get_historial_cortes():
        return execute_query("""
            SELECT * FROM cortes_caja
            ORDER BY fecha DESC
            LIMIT 50
        """)

    def crear_tabla_cortes():
        try:
            execute_query("""
                CREATE TABLE IF NOT EXISTS cortes_caja (
                    id              SERIAL PRIMARY KEY,
                    fecha           DATE NOT NULL,
                    total_ventas    INTEGER DEFAULT 0,
                    total_ingresos  NUMERIC(10,2) DEFAULT 0,
                    efectivo        NUMERIC(10,2) DEFAULT 0,
                    tarjeta         NUMERIC(10,2) DEFAULT 0,
                    observaciones   TEXT,
                    creado_en       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """, fetch=False)
        except:
            pass

    crear_tabla_cortes()

    # ── Labels reactivos ───────────────────────────────────
    lbl_ventas    = ft.Text("0", size=32, weight=ft.FontWeight.BOLD,
                            color=COLOR_ACENTO)
    lbl_ingresos  = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD,
                            color=COLOR_AZUL)
    lbl_efectivo  = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD,
                            color=COLOR_NARANJA)
    lbl_tarjeta   = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD,
                            color=COLOR_MORADO)
    lbl_fecha     = ft.Text(
        date.today().strftime("%A, %d de %B de %Y"),
        size=13, color=COLOR_SUBTEXTO
    )

    # ── Tabla historial ────────────────────────────────────
    tabla_historial = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ventas", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ingresos", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Efectivo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tarjeta", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Observaciones",
                                  weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("PDF", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.border.all(1, "#e0e0e0"),
        border_radius=10,
        heading_row_color="#f8f9fa",
        heading_row_height=44,
        data_row_min_height=48,
    )

    def refrescar():
        caja = get_caja_hoy()
        if caja:
            c = caja[0]
            lbl_ventas.value   = str(c["total_ventas"])
            lbl_ingresos.value = f"${c['total_ingresos']:.2f}"
            lbl_efectivo.value = f"${c['efectivo']:.2f}"
            lbl_tarjeta.value  = f"${c['tarjeta']:.2f}"

        tabla_historial.rows.clear()
        for corte in get_historial_cortes():
            ruta_pdf = f"cortes/corte_{corte['id']}.pdf"
            tabla_historial.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(
                        corte["fecha"].strftime("%d/%m/%Y"),
                        size=13, color=COLOR_TEXTO,
                        weight=ft.FontWeight.BOLD
                    )),
                    ft.DataCell(ft.Text(
                        str(corte["total_ventas"]),
                        size=13, color=COLOR_TEXTO
                    )),
                    ft.DataCell(ft.Text(
                        f"${corte['total_ingresos']:.2f}",
                        size=13, color=COLOR_ACENTO,
                        weight=ft.FontWeight.BOLD
                    )),
                    ft.DataCell(ft.Text(
                        f"${corte['efectivo']:.2f}",
                        size=13, color=COLOR_NARANJA
                    )),
                    ft.DataCell(ft.Text(
                        f"${corte['tarjeta']:.2f}",
                        size=13, color=COLOR_MORADO
                    )),
                    ft.DataCell(ft.Text(
                        corte["observaciones"] or "—",
                        size=12, color=COLOR_SUBTEXTO
                    )),
                    ft.DataCell(
                        ft.TextButton(
                            "📄 Ver",
                            on_click=lambda e, r=ruta_pdf: abrir_pdf(r)
                        ) if os.path.exists(ruta_pdf)
                        else ft.Text("—", color=COLOR_SUBTEXTO, size=12)
                    ),
                ])
            )
        page.update()

    def abrir_pdf(ruta):
        import subprocess
        subprocess.Popen(
            ["start", "", os.path.abspath(ruta)],
            shell=True
        )

    # ── Generar PDF del corte ──────────────────────────────
    def generar_pdf_corte(corte_id, datos, obs):
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(15, 15, 15)

            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "RestaurantePOS", ln=True, align="C")
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, "CORTE DE CAJA", ln=True, align="C")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6,
                     date.today().strftime("%d/%m/%Y"),
                     ln=True, align="C")
            pdf.cell(0, 6,
                     datetime.now().strftime("Hora: %H:%M:%S"),
                     ln=True, align="C")
            pdf.ln(4)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(6)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, "Resumen del día", ln=True)
            pdf.set_font("Helvetica", "", 11)

            items = [
                ("Total de ventas:",
                 str(datos["total_ventas"])),
                ("Ingresos totales:",
                 f"${datos['total_ingresos']:.2f}"),
                ("Pagos en efectivo:",
                 f"${datos['efectivo']:.2f}"),
                ("Pagos con tarjeta:",
                 f"${datos['tarjeta']:.2f}"),
            ]
            for label, valor in items:
                pdf.cell(120, 8, label)
                pdf.cell(0, 8, valor, ln=True)

            if obs:
                pdf.ln(4)
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 8, "Observaciones:", ln=True)
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 7, obs)

            pdf.ln(8)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(6)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 6, "Corte generado por RestaurantePOS",
                     ln=True, align="C")

            os.makedirs("cortes", exist_ok=True)
            ruta = f"cortes/corte_{corte_id}.pdf"
            pdf.output(ruta)
            return ruta
        except Exception as ex:
            print(f"Error PDF corte: {ex}")
            return None

    # ── Diálogo de corte ───────────────────────────────────
    campo_obs = ft.TextField(
        label="Observaciones (opcional)",
        multiline=True,
        min_lines=2,
        max_lines=4,
        border_radius=8,
        expand=True
    )

    def confirmar_corte(e):
        dialogo_corte.open = False
        page.update()
        ejecutar_corte()

    dialogo_corte = ft.AlertDialog(
        modal=True,
        title=ft.Text("🏧 Realizar Corte de Caja",
                      weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "¿Confirmas el corte de caja del día de hoy?",
                        size=13, color=COLOR_TEXTO
                    ),
                    ft.Text(
                        "Se guardará un registro con el resumen de ventas.",
                        size=12, color=COLOR_SUBTEXTO
                    ),
                    ft.Divider(),
                    campo_obs,
                ],
                spacing=10,
                tight=True
            ),
            width=400,
            padding=10
        ),
        actions=[
            ft.TextButton("Cancelar",
                          on_click=lambda e: cerrar_dialogo()),
            ft.ElevatedButton(
                "✅ Confirmar Corte",
                bgcolor=COLOR_ACENTO,
                color="white",
                on_click=confirmar_corte
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def cerrar_dialogo():
        dialogo_corte.open = False
        page.update()

    def abrir_dialogo_corte(e):
        campo_obs.value = ""
        if dialogo_corte not in page.overlay:
            page.overlay.append(dialogo_corte)
        dialogo_corte.open = True
        page.update()

    def ejecutar_corte():
        try:
            caja = get_caja_hoy()
            if not caja or caja[0]["total_ventas"] == 0:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(
                        "⚠️ No hay ventas hoy para hacer corte",
                        color="white"),
                    bgcolor=COLOR_NARANJA
                )
                page.snack_bar.open = True
                page.update()
                return

            c = caja[0]
            resultado = execute_query("""
                INSERT INTO cortes_caja
                    (fecha, total_ventas, total_ingresos,
                     efectivo, tarjeta, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, [
                date.today(),
                c["total_ventas"],
                c["total_ingresos"],
                c["efectivo"],
                c["tarjeta"],
                campo_obs.value.strip() or None
            ])

            corte_id = resultado[0]["id"]
            ruta_pdf = generar_pdf_corte(corte_id, c,
                                          campo_obs.value.strip())

            refrescar()

            def abrir(e):
                if ruta_pdf:
                    abrir_pdf(ruta_pdf)
                dialogo_ok.open = False
                page.update()

            dialogo_ok = ft.AlertDialog(
                modal=True,
                title=ft.Text("✅ Corte Realizado",
                              weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    controls=[
                        ft.Text(f"Corte #{corte_id} guardado",
                                size=14, color=COLOR_TEXTO),
                        ft.Text(
                            f"Total ingresos: ${c['total_ingresos']:.2f}",
                            size=13, color=COLOR_ACENTO,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            f"Ventas: {c['total_ventas']}",
                            size=13, color=COLOR_SUBTEXTO
                        ),
                    ],
                    spacing=8,
                    tight=True
                ),
                actions=[
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda e: setattr(
                            dialogo_ok, 'open', False) or page.update()
                    ),
                    ft.ElevatedButton(
                        "📄 Ver PDF",
                        bgcolor=COLOR_AZUL,
                        color="white",
                        on_click=abrir
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            if dialogo_ok not in page.overlay:
                page.overlay.append(dialogo_ok)
            dialogo_ok.open = True
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Error: {ex}", color="white"),
                bgcolor=COLOR_ROJO
            )
            page.snack_bar.open = True
            page.update()

    # ── Tarjeta resumen ────────────────────────────────────
    def tarjeta(icono, titulo, lbl, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icono, size=26),
                    lbl,
                    ft.Text(titulo, size=12, color=COLOR_SUBTEXTO),
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

    refrescar()

    # ── Layout ─────────────────────────────────────────────
    return ft.Column(
        controls=[
            # Header
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("🏧 Caja", size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_TEXTO),
                            lbl_fecha,
                        ],
                        spacing=2
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "✂️ Realizar Corte de Caja",
                        bgcolor=COLOR_ACENTO,
                        color="white",
                        height=42,
                        on_click=abrir_dialogo_corte
                    ),
                ]
            ),
            ft.Container(height=8),
            # Tarjetas resumen hoy
            ft.Text("📊 Resumen de Hoy", size=15,
                    weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
            ft.Container(height=4),
            ft.Row(
                controls=[
                    tarjeta("🧾", "Total Ventas",
                            lbl_ventas, COLOR_ACENTO),
                    tarjeta("💰", "Ingresos Totales",
                            lbl_ingresos, COLOR_AZUL),
                    tarjeta("💵", "En Efectivo",
                            lbl_efectivo, COLOR_NARANJA),
                    tarjeta("💳", "Con Tarjeta",
                            lbl_tarjeta, COLOR_MORADO),
                ],
                spacing=12
            ),
            ft.Container(height=16),
            # Historial de cortes
            ft.Text("📅 Historial de Cortes", size=15,
                    weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
            ft.Container(height=4),
            ft.Container(
                content=ft.ListView(
                    controls=[tabla_historial],
                    expand=True
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
        ],
        expand=True,
        spacing=0
    )
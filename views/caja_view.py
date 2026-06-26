# views/caja_view.py
import flet as ft
import os
from datetime import datetime, date
from database.db_manager import (
    get_resumen_dia, get_cortes_caja, crear_corte_caja, get_ventas
)

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

    lbl_ventas   = ft.Text("0", size=32, weight=ft.FontWeight.BOLD,
                           color=COLOR_ACENTO)
    lbl_ingresos = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD,
                           color=COLOR_AZUL)
    lbl_efectivo = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD,
                           color=COLOR_NARANJA)
    lbl_tarjeta  = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD,
                           color=COLOR_MORADO)
    lbl_fecha    = ft.Text(
        date.today().strftime("%A, %d de %B de %Y"),
        size=13, color=COLOR_SUBTEXTO
    )

    def abrir_pdf(ruta):
        try:
            import subprocess

            if os.path.exists(ruta):
                subprocess.Popen(
                    ["start", "", os.path.abspath(ruta)],
                    shell=True
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(
                        f"No existe el archivo:\n{ruta}",
                        color="white"
                    ),
                    bgcolor=COLOR_ROJO
                )
                page.snack_bar.open = True
                page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    f"Error al abrir PDF: {ex}",
                    color="white"
                ),
                bgcolor=COLOR_ROJO
            )
            page.snack_bar.open = True
            page.update()

    historial_list = ft.Column(spacing=8,
                               scroll=ft.ScrollMode.AUTO,
                               expand=True)

    fecha_filtro = ft.TextField(
        label="Buscar por fecha (AAAA-MM-DD)",
        hint_text="2026-06-19",
        height=48,
        width=250,
        on_submit=lambda e: refrescar(fecha_filtro.value.strip())
    )

    def limpiar_filtro(e):
        fecha_filtro.value = ""
        refrescar()

    def abrir_ventas_del_dia(fecha):
        ventas = get_ventas(fecha, fecha)

        filas = []
        for v in ventas:
            filas.append(
                ft.Row(
                    controls=[
                        ft.Text(f"#{str(v.get('id', ''))[:8]}", size=12,
                                 color=COLOR_TEXTO, weight=ft.FontWeight.BOLD, width=80),
                        ft.Container(
                            content=ft.Text(
                                "💵" if v.get("metodo_pago") == "efectivo" else "💳",
                                size=12, color="white"),
                            bgcolor=COLOR_NARANJA if v.get("metodo_pago") == "efectivo" else COLOR_MORADO,
                            border_radius=16, padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        ),
                        ft.Text(f"${v.get('total', 0):.2f}", size=13, color=COLOR_TEXTO,
                                 weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.RIGHT),
                    ],
                    spacing=10,
                )
            )

        if not filas:
            filas = [ft.Text("Sin ventas registradas en esta fecha", color=COLOR_SUBTEXTO, italic=True)]

        total_dia = sum(v.get("total", 0) for v in ventas)

        def cerrar(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"🧾 Ventas del {fecha}"),
            content=ft.Container(
                width=380,
                content=ft.Column(
                    controls=[
                        ft.Column(controls=filas, spacing=8, scroll=ft.ScrollMode.AUTO,
                                   height=min(320, 40 + 36 * max(len(filas), 1))),
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                ft.Text("TOTAL", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                                ft.Text(f"${total_dia:.2f}", size=16, weight=ft.FontWeight.BOLD, color=COLOR_ACENTO),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                    ],
                    spacing=8,
                    tight=True,
                ),
            ),
            actions=[ft.TextButton("Cerrar", on_click=cerrar)],
        )
        if dialogo not in page.overlay:
            page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def refrescar(filtro_fecha=None):
        resumen = get_resumen_dia()

        lbl_ventas.value = str(resumen.get("total_ventas", 0))
        lbl_ingresos.value = f"${resumen.get('total', 0):.2f}"
        lbl_efectivo.value = f"${resumen.get('efectivo', 0):.2f}"
        lbl_tarjeta.value = f"${resumen.get('tarjeta', 0):.2f}"

        if filtro_fecha:
            cortes = get_cortes_caja(
                desde=filtro_fecha,
                hasta=filtro_fecha
            )
        else:
            cortes = get_cortes_caja()

        historial_list.controls.clear()

        if cortes:
            for c in cortes:
                corte_id = c.get("id", "")
                ruta_pdf = f"cortes/corte_{corte_id}.pdf"

                historial_list.controls.append(
                    ft.Container(
                        bgcolor=COLOR_FONDO,
                        border_radius=10,
                        padding=16,
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"📅 {c.get('fecha', '')}",
                                            size=15,
                                            color=COLOR_TEXTO,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        ft.Container(expand=True),
                                        ft.Text(
                                            f"${c.get('total_ingresos', 0):.2f}",
                                            size=18,
                                            color=COLOR_ACENTO,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                    ]
                                ),

                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            f"🧾 {c.get('total_ventas', 0)} ventas",
                                            size=12,
                                            color=COLOR_SUBTEXTO
                                        ),

                                        ft.Text(
                                            f"💵 ${c.get('efectivo', 0):.2f}",
                                            size=12,
                                            color=COLOR_NARANJA
                                        ),

                                        ft.Text(
                                            f"💳 ${c.get('tarjeta', 0):.2f}",
                                            size=12,
                                            color=COLOR_MORADO
                                        ),

                                        ft.Container(expand=True),

                                        ft.TextButton(
                                            "🧾 Ver ventas",
                                            on_click=lambda e, fecha=c.get("fecha", ""):
                                                abrir_ventas_del_dia(fecha)
                                        ),

                                        ft.TextButton(
                                            "📄 Ver/Imprimir",
                                            on_click=lambda e, r=ruta_pdf:
                                                abrir_pdf(r)
                                        ) if os.path.exists(ruta_pdf)
                                        else ft.Text(
                                            "Sin PDF",
                                            size=11,
                                            color=COLOR_SUBTEXTO
                                        ),
                                    ],
                                    spacing=16
                                ),

                                ft.Text(
                                    f"📝 {c.get('observaciones', '')}",
                                    size=11,
                                    color=COLOR_SUBTEXTO,
                                    italic=True
                                ) if c.get("observaciones")
                                else ft.Container(height=0),
                            ],
                            spacing=6
                        ),
                    )
                )

        else:
            historial_list.controls.append(
                ft.Text(
                    "Sin cortes registrados en este rango",
                    color=COLOR_SUBTEXTO,
                    italic=True
                )
            )

        page.update()
    
    def generar_pdf_corte(corte_id, resumen, obs, ventas_dia):
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
            pdf.cell(0, 6, date.today().strftime("%d/%m/%Y"),
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
                ("Total de ventas:", str(resumen.get("total_ventas", 0))),
                ("Ingresos totales:", f"${resumen.get('total', 0):.2f}"),
                ("Pagos en efectivo:", f"${resumen.get('efectivo', 0):.2f}"),
                ("Pagos con tarjeta:", f"${resumen.get('tarjeta', 0):.2f}"),
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

            if ventas_dia:
                pdf.ln(6)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 8, "Detalle de ventas del día", ln=True)
                pdf.ln(1)

                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(30, 7, "Hora", border=0)
                pdf.cell(70, 7, "Venta #", border=0)
                pdf.cell(40, 7, "Método", border=0)
                pdf.cell(40, 7, "Total", border=0, align="R")
                pdf.ln()
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(2)

                pdf.set_font("Helvetica", "", 9)
                for v in ventas_dia:
                    hora = str(v.get("creado_en", ""))[-8:] if v.get("creado_en") else "—"
                    folio = f"#{str(v.get('id', ''))[:10]}"
                    metodo = "Efectivo" if v.get("metodo_pago") == "efectivo" else "Tarjeta"
                    total = f"${v.get('total', 0):.2f}"

                    pdf.cell(30, 6, hora, border=0)
                    pdf.cell(70, 6, folio, border=0)
                    pdf.cell(40, 6, metodo, border=0)
                    pdf.cell(40, 6, total, border=0, align="R")
                    pdf.ln()

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

    campo_obs = ft.TextField(
        label="Observaciones (opcional)",
        multiline=True, min_lines=2, max_lines=4,
        border_radius=8, expand=True
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
                        "¿Confirmas el corte de caja del día?",
                        size=13, color=COLOR_TEXTO),
                    ft.Text(
                        "Se guardará un registro con el resumen.",
                        size=12, color=COLOR_SUBTEXTO),
                    ft.Divider(),
                    campo_obs,
                ],
                spacing=10, tight=True
            ),
            width=400, padding=10
        ),
        actions=[
            ft.TextButton("Cancelar",
                          on_click=lambda e: cerrar_dialogo()),
            ft.ElevatedButton(
                "✅ Confirmar Corte",
                bgcolor=COLOR_ACENTO, color="white",
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
            resumen = get_resumen_dia()
            if not resumen or resumen.get("total_ventas", 0) == 0:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(
                        "⚠️ No hay ventas hoy para hacer corte",
                        color="white"),
                    bgcolor=COLOR_NARANJA
                )
                page.snack_bar.open = True
                page.update()
                return

            datos_corte = {
                "fecha": str(date.today()),
                "total_ventas": resumen.get("total_ventas", 0),
                "total_ingresos": resumen.get("total", 0),
                "efectivo": resumen.get("efectivo", 0),
                "tarjeta": resumen.get("tarjeta", 0),
            }
            obs = campo_obs.value.strip()
            if obs:
                datos_corte["observaciones"] = obs

            ventas_dia = get_ventas(str(date.today()), str(date.today()))

            corte_id = crear_corte_caja(datos_corte)
            ruta_pdf = generar_pdf_corte(
                corte_id, resumen, campo_obs.value.strip(), ventas_dia)

            refrescar()

            def abrir(e):
                if ruta_pdf:
                    abrir_pdf(ruta_pdf)
                dialogo_ok.open = False
                page.update()

            filas_desglose = []
            for v in ventas_dia:
                filas_desglose.append(
                    ft.Row(
                        controls=[
                            ft.Text(f"#{str(v.get('id', ''))[:8]}", size=12,
                                     color=COLOR_TEXTO, weight=ft.FontWeight.BOLD, width=70),
                            ft.Container(
                                content=ft.Text(
                                    "💵" if v.get("metodo_pago") == "efectivo" else "💳",
                                    size=11, color="white"),
                                bgcolor=COLOR_NARANJA if v.get("metodo_pago") == "efectivo" else COLOR_MORADO,
                                border_radius=14, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            ),
                            ft.Text(f"${v.get('total', 0):.2f}", size=13, color=COLOR_TEXTO,
                                     weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.RIGHT),
                        ],
                        spacing=8,
                    )
                )

            if not filas_desglose:
                filas_desglose = [ft.Text("Sin ventas registradas", color=COLOR_SUBTEXTO, italic=True, size=12)]

            dialogo_ok = ft.AlertDialog(
                modal=True,
                title=ft.Text("✅ Corte Realizado",
                              weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=380,
                    content=ft.Column(
                        controls=[
                            ft.Text(f"Corte guardado",
                                    size=14, color=COLOR_TEXTO),
                            ft.Text(
                                f"Total ingresos: ${resumen.get('total', 0):.2f}",
                                size=13, color=COLOR_ACENTO,
                                weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"Ventas: {resumen.get('total_ventas', 0)}",
                                size=13, color=COLOR_SUBTEXTO),
                            ft.Divider(),
                            ft.Text("Desglose de ventas", size=13,
                                    weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                            ft.Column(
                                controls=filas_desglose,
                                spacing=6,
                                scroll=ft.ScrollMode.AUTO,
                                height=min(260, 36 + 30 * max(len(filas_desglose), 1)),
                            ),
                        ],
                        spacing=8, tight=True
                    ),
                    padding=ft.padding.only(top=4),
                ),
                actions=[
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda e: setattr(
                            dialogo_ok, 'open', False) or page.update()
                    ),
                    ft.ElevatedButton(
                        "📄 Ver PDF",
                        bgcolor=COLOR_AZUL, color="white",
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
            import traceback
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Error: {ex}", color="white"),
                bgcolor=COLOR_ROJO
            )
            page.snack_bar.open = True
            page.update()

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
            width=200,
            height=120,
            shadow=ft.BoxShadow(
                blur_radius=8, color="#00000010",
                offset=ft.Offset(0, 2)
            )
        )

    refrescar()

    return ft.Column(
        controls=[
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
                        bgcolor=COLOR_ACENTO, color="white",
                        height=42, on_click=abrir_dialogo_corte
                    ),
                ]
            ),
            ft.Container(height=8),
            ft.Text("📊 Resumen de Hoy", size=15,
                    weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
            ft.Container(height=4),
            ft.Row(
                controls=[
                    tarjeta("🧾", "Total Ventas", lbl_ventas, COLOR_ACENTO),
                    tarjeta("💰", "Ingresos Totales", lbl_ingresos, COLOR_AZUL),
                    tarjeta("💵", "En Efectivo", lbl_efectivo, COLOR_NARANJA),
                    tarjeta("💳", "Con Tarjeta", lbl_tarjeta, COLOR_MORADO),
                ],
                spacing=12, wrap=True
            ),
            ft.Container(height=16),
            ft.Row(
                controls=[
                    ft.Text("📅 Historial de Cortes", size=15,
                            weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                    ft.Container(expand=True),
                    fecha_filtro,
                    ft.ElevatedButton(
                        "🔍 Buscar",
                        bgcolor=COLOR_AZUL, color="white",
                        height=48,
                        on_click=lambda e: refrescar(fecha_filtro.value.strip())
                    ),
                    ft.TextButton(
                        "✖️ Limpiar",
                        on_click=limpiar_filtro
                    ),
                ],
                spacing=8
            ),
            ft.Container(height=4),
            ft.Container(
                content=historial_list,
                bgcolor=COLOR_TARJETA,
                border_radius=14,
                padding=16,
                expand=True,
                shadow=ft.BoxShadow(
                    blur_radius=8, color="#00000010",
                    offset=ft.Offset(0, 2)
                )
            )
        ],
        expand=True,
        spacing=0
    )
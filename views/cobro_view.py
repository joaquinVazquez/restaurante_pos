# views/cobro_view.py
import flet as ft
import os
from datetime import datetime
from database.db_manager import crear_venta

COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#ffffff"
COLOR_ACENTO     = "#00b894"
COLOR_ROJO       = "#e74c3c"
COLOR_AZUL       = "#3498db"
COLOR_NARANJA    = "#ff7a00"
COLOR_FONDO      = "#f0f4f8"


def cobro_view(page: ft.Page, carrito, on_venta_completada):

    metodo_pago    = {"valor": "efectivo"}
    monto_recibido = {"valor": 0.0}
    total          = carrito.total()

    lbl_cambio = ft.Text("$0.00", size=22,
                         weight=ft.FontWeight.BOLD,
                         color=COLOR_ACENTO)
    lbl_estado = ft.Text("", size=13, color=COLOR_ROJO)

    # ── Resumen orden ──────────────────────────────────────
    filas_orden = []
    for pid, item in carrito.items.items():
        sub = item["precio"] * item["cantidad"]
        filas_orden.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(item["nombre"], size=13,
                                color=COLOR_TEXTO, expand=True,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"x{item['cantidad']}",
                                size=12, color=COLOR_SUBTEXTO,
                                width=30),
                        ft.Text(f"${sub:.2f}", size=13,
                                color=COLOR_TEXTO,
                                weight=ft.FontWeight.BOLD,
                                width=65,
                                text_align=ft.TextAlign.RIGHT),
                    ],
                ),
                bgcolor=COLOR_FONDO,
                border_radius=8,
                padding=ft.padding.symmetric(
                    horizontal=12, vertical=8)
            )
        )

    # ── Campo monto ────────────────────────────────────────
    campo_monto = ft.TextField(
        label="Monto recibido",
        prefix_text="$",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        expand=True,
        bgcolor="white",
        on_change=lambda e: calcular_cambio(e)
    )

    def calcular_cambio(e):
        try:
            monto = float(campo_monto.value or 0)
            monto_recibido["valor"] = monto
            cambio = monto - total
            if cambio >= 0:
                lbl_cambio.value = f"${cambio:.2f}"
                lbl_cambio.color = COLOR_ACENTO
                lbl_estado.value = ""
            else:
                lbl_cambio.value = f"-${abs(cambio):.2f}"
                lbl_cambio.color = COLOR_ROJO
                lbl_estado.value = "⚠️ Monto insuficiente"
        except ValueError:
            lbl_cambio.value = "$0.00"
        page.update()

    # ── Botones método pago ────────────────────────────────
    btn_efectivo = ft.ElevatedButton(
        "💵 Efectivo",
        bgcolor=COLOR_ACENTO,
        color="white",
        expand=True,
        height=48,
        on_click=lambda e: seleccionar_metodo("efectivo")
    )
    btn_tarjeta = ft.ElevatedButton(
        "💳 Tarjeta",
        bgcolor="#e0e0e0",
        color=COLOR_TEXTO,
        expand=True,
        height=48,
        on_click=lambda e: seleccionar_metodo("tarjeta")
    )

    contenedor_efectivo = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[campo_monto]),
                ft.Row(
                    controls=[
                        ft.Text("Cambio:", size=14,
                                color=COLOR_SUBTEXTO),
                        lbl_cambio
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                lbl_estado
            ],
            spacing=10
        ),
        visible=True
    )

    def seleccionar_metodo(metodo):
        metodo_pago["valor"] = metodo
        if metodo == "efectivo":
            btn_efectivo.bgcolor        = COLOR_ACENTO
            btn_efectivo.color          = "white"
            btn_tarjeta.bgcolor         = "#e0e0e0"
            btn_tarjeta.color           = COLOR_TEXTO
            contenedor_efectivo.visible = True
        else:
            btn_tarjeta.bgcolor         = COLOR_ACENTO
            btn_tarjeta.color           = "white"
            btn_efectivo.bgcolor        = "#e0e0e0"
            btn_efectivo.color          = COLOR_TEXTO
            contenedor_efectivo.visible = False
        page.update()

    # ── Generar PDF ────────────────────────────────────────
    def generar_ticket_pdf(venta_id):
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(15, 15, 15)

            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "RestaurantePOS",
                     ln=True, align="C")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, "Ticket de Venta",
                     ln=True, align="C")
            pdf.cell(0, 6,
                     datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                     ln=True, align="C")
            pdf.cell(0, 6, f"Venta #: {venta_id}",
                     ln=True, align="C")
            pdf.ln(4)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(4)

            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(90, 7, "Producto", border=0)
            pdf.cell(25, 7, "Cant.", border=0, align="C")
            pdf.cell(35, 7, "Precio", border=0, align="R")
            pdf.cell(35, 7, "Subtotal", border=0, align="R")
            pdf.ln()
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2)

            pdf.set_font("Helvetica", "", 10)
            for pid, item in carrito.items.items():
                sub = item["precio"] * item["cantidad"]
                pdf.cell(90, 7, item["nombre"][:35], border=0)
                pdf.cell(25, 7, str(item["cantidad"]),
                         border=0, align="C")
                pdf.cell(35, 7, f"${item['precio']:.2f}",
                         border=0, align="R")
                pdf.cell(35, 7, f"${sub:.2f}",
                         border=0, align="R")
                pdf.ln()

            pdf.ln(2)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(4)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(150, 8, "TOTAL:", border=0, align="R")
            pdf.cell(35, 8, f"${total:.2f}",
                     border=0, align="R")
            pdf.ln()

            pdf.set_font("Helvetica", "", 10)
            pdf.cell(
                150, 7,
                f"Método: {metodo_pago['valor'].capitalize()}",
                border=0, align="R"
            )
            pdf.ln()

            if metodo_pago["valor"] == "efectivo":
                pdf.cell(
                    150, 7,
                    f"Recibido: ${monto_recibido['valor']:.2f}",
                    border=0, align="R"
                )
                pdf.ln()
                cambio = monto_recibido["valor"] - total
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(150, 7, f"Cambio: ${cambio:.2f}",
                         border=0, align="R")
                pdf.ln()

            pdf.ln(6)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 6, "¡Gracias por su compra!",
                     ln=True, align="C")

            os.makedirs("tickets", exist_ok=True)
            ruta = f"tickets/ticket_{venta_id}.pdf"
            pdf.output(ruta)
            return ruta
        except Exception as ex:
            print(f"Error PDF: {ex}")
            return None

    # ── Confirmar venta ────────────────────────────────────
    def confirmar_venta(e):
        if metodo_pago["valor"] == "efectivo":
            try:
                monto = float(campo_monto.value or 0)
                if monto < total:
                    lbl_estado.value = "⚠️ Monto insuficiente"
                    page.update()
                    return
            except ValueError:
                lbl_estado.value = "⚠️ Ingresa un monto válido"
                page.update()
                return

        try:
            # ── Armar datos ────────────────────────────────
            monto_r  = monto_recibido["valor"] \
                if metodo_pago["valor"] == "efectivo" else None
            cambio_r = (monto_recibido["valor"] - total) \
                if metodo_pago["valor"] == "efectivo" else None

            datos = {
                "total":          total,
                "metodo_pago":    metodo_pago["valor"],
                "monto_recibido": monto_r,
                "cambio":         cambio_r,
            }

            # ── Armar items ────────────────────────────────
            items = [
                {
                    "producto_id":    str(pid),
                    "cantidad":       item["cantidad"],
                    "precio_unitario": item["precio"],
                    "subtotal":       item["precio"] * item["cantidad"],
                }
                for pid, item in carrito.items.items()
            ]

            # ── Crear venta en Convex o SQLite ─────────────
            venta_id = crear_venta(datos, items)

            # ── Generar PDF ────────────────────────────────
            ruta_pdf = generar_ticket_pdf(venta_id)

            # ── Diálogo éxito ──────────────────────────────
            def cerrar_y_volver(e):
                dialogo_ok.open = False
                carrito.vaciar()
                on_venta_completada()
                page.update()

            def abrir_pdf(e):
                if ruta_pdf:
                    import subprocess
                    subprocess.Popen(
                        ["start", "", os.path.abspath(ruta_pdf)],
                        shell=True
                    )

            dialogo_ok = ft.AlertDialog(
                modal=True,
                title=ft.Text("✅ Venta Completada",
                              weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"Venta #{venta_id} registrada",
                            size=14, color=COLOR_TEXTO),
                        ft.Text(f"Total: ${total:.2f}",
                                size=13, color=COLOR_ACENTO,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"Cambio: ${(monto_recibido['valor'] - total):.2f}"
                            if metodo_pago["valor"] == "efectivo"
                            else "Pago con tarjeta ✅",
                            size=13, color=COLOR_SUBTEXTO),
                    ],
                    spacing=8,
                    tight=True
                ),
                actions=[
                    ft.TextButton("Nueva Venta",
                                  on_click=cerrar_y_volver),
                    ft.ElevatedButton(
                        "📄 Ver Ticket",
                        bgcolor=COLOR_AZUL,
                        color="white",
                        on_click=abrir_pdf
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
                content=ft.Text(f"❌ Error: {ex}",
                                color="white"),
                bgcolor=COLOR_ROJO
            )
            page.snack_bar.open = True
            page.update()

    # ── Layout ─────────────────────────────────────────────
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("💳 Cobro", size=22,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_TEXTO),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "← Regresar",
                        on_click=lambda e: on_venta_completada(),
                        style=ft.ButtonStyle(color=COLOR_SUBTEXTO)
                    )
                ]
            ),
            ft.Container(height=8),
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("📋 Resumen", size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_TEXTO),
                                ft.Divider(),
                                ft.Column(
                                    controls=filas_orden,
                                    scroll=ft.ScrollMode.AUTO,
                                    expand=True,
                                    spacing=4
                                ),
                                ft.Divider(),
                                ft.Row(
                                    controls=[
                                        ft.Text("TOTAL", size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=COLOR_TEXTO),
                                        ft.Text(f"${total:.2f}",
                                                size=22,
                                                weight=ft.FontWeight.BOLD,
                                                color=COLOR_ACENTO)
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ],
                            spacing=8,
                            expand=True
                        ),
                        expand=3,
                        bgcolor=COLOR_TARJETA,
                        border_radius=14,
                        padding=16,
                        shadow=ft.BoxShadow(
                            blur_radius=8,
                            color="#00000010",
                            offset=ft.Offset(0, 2)
                        )
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("💰 Método de Pago",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_TEXTO),
                                ft.Divider(),
                                ft.Row(
                                    controls=[
                                        btn_efectivo,
                                        btn_tarjeta
                                    ],
                                    spacing=10
                                ),
                                ft.Container(height=8),
                                contenedor_efectivo,
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    "✅  CONFIRMAR VENTA",
                                    bgcolor=COLOR_ACENTO,
                                    color="white",
                                    height=55,
                                    expand=True,
                                    on_click=confirmar_venta,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(
                                            radius=10)
                                    )
                                )
                            ],
                            spacing=8,
                            expand=True
                        ),
                        expand=2,
                        bgcolor=COLOR_TARJETA,
                        border_radius=14,
                        padding=16,
                        shadow=ft.BoxShadow(
                            blur_radius=8,
                            color="#00000010",
                            offset=ft.Offset(0, 2)
                        )
                    )
                ],
                expand=True,
                spacing=16
            )
        ],
        expand=True,
        spacing=0
    )
import flet as ft
from datetime import date

from database.db_manager import (
    get_reporte_ventas, get_reporte_margen,
    get_gastos, crear_gasto,
    get_mermas, crear_merma,
    get_comparativa, get_cortes_caja,
    get_productos, get_ventas,
    get_detalle_venta, get_productos_mas_vendidos,
)
from utils.graficas import grafica_barras_comparativa, grafica_productos_top

CATEGORIAS_GASTO = ["Insumos", "Renta", "Servicios", "Personal", "Otros"]

COLOR_TEXTO    = "#2c3e50"
COLOR_SUBTEXTO = "#7f8c8d"
COLOR_ACENTO   = "#00b894"
COLOR_ROJO     = "#e74c3c"
COLOR_AZUL     = "#3498db"
COLOR_TARJETA  = "#ffffff"
COLOR_FONDO    = "#f0f4f8"

def reportes_view(page: ft.Page):
    hoy = date.today()

    def snack(texto, color=COLOR_ACENTO):
        page.snack_bar = ft.SnackBar(content=ft.Text(texto, color="white"), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def card(content):
        return ft.Container(
            content=content,
            bgcolor=COLOR_TARJETA,
            border_radius=12,
            padding=16,
            expand=True,
        )

    # UX FIX: Quitamos expand=True y asignamos width fijos para permitir el Wrap
    desde = ft.TextField(label="Desde", value=str(hoy), width=180)
    hasta = ft.TextField(label="Hasta", value=str(hoy), width=180)

    def rango():
        return desde.value, hasta.value

    # ════════════════════ TAB 1: VENTAS ═══════════════════
    ventas_stats   = ft.Row(spacing=12, wrap=True, run_spacing=12)
    cortes_list    = ft.Column(spacing=8)
    historial_list = ft.Column(spacing=8)

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
            bgcolor=COLOR_FONDO, border_radius=10, padding=14, width=160, height=90,
        )

    def abrir_detalle_venta(venta):
        items = get_detalle_venta(venta["id"])

        filas = []
        for item in items:
            filas.append(
                ft.Row(
                    controls=[
                        ft.Text(item["producto_nombre"], size=13, color=COLOR_TEXTO,
                                 expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"x{item['cantidad']}", size=12, color=COLOR_SUBTEXTO, width=40),
                        ft.Text(f"${item['precio_unitario']:.2f}", size=12, color=COLOR_SUBTEXTO, width=60, text_align=ft.TextAlign.RIGHT),
                        ft.Text(f"${item['subtotal']:.2f}", size=13, color=COLOR_TEXTO, weight=ft.FontWeight.BOLD, width=70, text_align=ft.TextAlign.RIGHT),
                    ],
                    spacing=8,
                )
            )

        if not filas:
            filas = [ft.Text("No se encontraron productos para esta venta", color=COLOR_SUBTEXTO, italic=True)]

        def cerrar(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"🧾 Venta #{str(venta['id'])[:8]}"),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    controls=[
                        ft.Text(f"Fecha: {venta['creado_en']}", size=12, color=COLOR_SUBTEXTO),
                        ft.Text(
                            "💵 Efectivo" if venta["metodo_pago"] == "efectivo" else "💳 Tarjeta",
                            size=12, color=COLOR_SUBTEXTO),
                        ft.Divider(),
                        ft.Column(controls=filas, spacing=6, scroll=ft.ScrollMode.AUTO,
                                   height=min(280, 40 + 32 * max(len(filas), 1))),
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                ft.Text("TOTAL", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                                ft.Text(f"${venta['total']:.2f}", size=16, weight=ft.FontWeight.BOLD, color=COLOR_ACENTO),
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

    def cargar_ventas():
        d, h = rango()
        data    = get_reporte_ventas(d, h)
        cortes  = get_cortes_caja(d, h)
        ventas  = [v for v in get_ventas(d, h)]

        ventas_stats.controls = [
            stat_box("💰", "Ingresos", f"${data.get('ingresos', 0):.2f}", COLOR_ACENTO),
            stat_box("🧾", "Ventas", str(data.get('cantidad_ventas', 0)), COLOR_AZUL),
            stat_box("💵", "Efectivo", f"${data.get('efectivo', 0):.2f}", COLOR_TEXTO),
            stat_box("💳", "Tarjeta", f"${data.get('tarjeta', 0):.2f}", COLOR_TEXTO),
        ]

        if cortes:
            cortes_list.controls = [
                ft.Container(
                    bgcolor=COLOR_FONDO, border_radius=8, padding=12,
                    content=ft.Row(
                        controls=[
                            ft.Text(str(c.get("fecha", "")), expand=True, size=13),
                            ft.Text(f"🧾 {c.get('total_ventas', 0)}", size=12, color=COLOR_SUBTEXTO, width=70),
                            ft.Text(f"${c.get('total_ingresos', 0):.2f}", weight=ft.FontWeight.BOLD, size=13, color=COLOR_ACENTO),
                        ],
                    ),
                ) for c in cortes
            ]
        else:
            cortes_list.controls = [ft.Text("Sin cortes de caja en este rango", color=COLOR_SUBTEXTO, italic=True)]

        if ventas:
            historial_list.controls = [
                ft.Container(
                    bgcolor=COLOR_FONDO, border_radius=8, padding=12,
                    on_click=lambda e, venta=v: abrir_detalle_venta(venta),
                    ink=True,
                    content=ft.Row(
                        controls=[
                            ft.Text(f"#{str(v['id'])[:8]}", size=12, color=COLOR_TEXTO, weight=ft.FontWeight.BOLD, width=80),
                            ft.Text(str(v["creado_en"]), size=12, color=COLOR_SUBTEXTO, expand=True),
                            ft.Container(
                                content=ft.Text("💵 Efectivo" if v["metodo_pago"] == "efectivo" else "💳 Tarjeta", size=11, color="white"),
                                bgcolor=COLOR_ACENTO if v["metodo_pago"] == "efectivo" else COLOR_AZUL,
                                border_radius=20, padding=ft.padding.symmetric(horizontal=8, vertical=4)),
                            ft.Text(f"${v['total']:.2f}", size=13, color=COLOR_ACENTO, weight=ft.FontWeight.BOLD, width=80, text_align=ft.TextAlign.RIGHT),
                            ft.Icon(ft.icons.CHEVRON_RIGHT, color=COLOR_SUBTEXTO, size=18),
                        ],
                        spacing=10
                    ),
                ) for v in ventas
            ]
        else:
            historial_list.controls = [ft.Text("Sin ventas en este rango", color=COLOR_SUBTEXTO, italic=True)]
        page.update()

    ventas_tab = card(
        ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(content=ft.Text("📊 Ventas y Cortes de Caja", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO), height=30),
                ft.Row([
                    desde, hasta,
                    ft.ElevatedButton("🔄 Actualizar", height=48, bgcolor=COLOR_ACENTO, color="white", on_click=lambda e: cargar_todo())
                ], spacing=12, wrap=True),
                ventas_stats,
                ft.Divider(),
                ft.Text("Historial de Ventas", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                historial_list,
                ft.Divider(),
                ft.Text("Historial de Cortes de Caja", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                cortes_list,
            ],
            spacing=14,
        )
    )

    # ════════════════════ TAB 2: MARGEN ═══════════════════
    margen_content = ft.Column(spacing=10)

    def cargar_margen():
        d, h = rango()
        data = get_reporte_margen(d, h)
        ganancia = data.get("ganancia_neta", 0)
        color_ganancia = COLOR_ACENTO if ganancia >= 0 else COLOR_ROJO

        margen_content.controls = [
            ft.Row([
                stat_box("💰", "Ingresos", f"${data.get('ingresos', 0):.2f}", COLOR_AZUL),
                stat_box("📦", "Costo Productos", f"${data.get('costo_productos', 0):.2f}", COLOR_TEXTO),
            ], spacing=12, wrap=True),
            ft.Row([
                stat_box("🧾", "Gastos", f"${data.get('gastos', 0):.2f}", "#e67e22"),
                stat_box("📉", "Merma", f"${data.get('merma', 0):.2f}", COLOR_ROJO),
            ], spacing=12, wrap=True),
            ft.Divider(),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Ganancia Neta", size=14, color=COLOR_SUBTEXTO),
                        ft.Text(f"${ganancia:.2f}", size=32, weight=ft.FontWeight.BOLD, color=color_ganancia),
                        ft.Text(f"Margen: {data.get('margen_pct', 0):.1f}%", size=14, color=COLOR_SUBTEXTO),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=COLOR_FONDO, border_radius=12, padding=20, alignment=ft.alignment.center,
            )
        ]
        page.update()

    margen_tab = card(
        ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("📈 Margen Real de Ganancia", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Text("Ingresos - Costos - Gastos - Merma", size=12, color=COLOR_SUBTEXTO),
                margen_content,
            ],
            spacing=14,
        )
    )

    # ════════════════════ TAB 3: GASTOS ═══════════════════
    gastos_list = ft.Column(spacing=8)
    gasto_categoria = ft.Dropdown(
        label="Categoría", value="Insumos", width=180,
        options=[ft.dropdown.Option(c) for c in CATEGORIAS_GASTO])
    
    
    # UX FIX: width fijo en lugar de expand=True
    gasto_desc  = ft.TextField(label="Descripción", height=48, width=220)
    gasto_monto = ft.TextField(label="Monto", prefix_text="$", height=48, width=140, keyboard_type=ft.KeyboardType.NUMBER)

    def cargar_gastos():
        d, h = rango()
        gastos = get_gastos(d, h)
        if gastos:
            gastos_list.controls = [
                ft.Container(
                    bgcolor=COLOR_FONDO, border_radius=8, padding=12,
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(g["categoria"], size=11, color="white"),
                            bgcolor="#e67e22", border_radius=6, padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        ),
                        ft.Text(g["descripcion"], expand=True, size=13),
                        ft.Text(f"${g['monto']:.2f}", weight=ft.FontWeight.BOLD, color=COLOR_ROJO, size=13),
                    ], spacing=10),
                ) for g in gastos
            ]
        else:
            gastos_list.controls = [ft.Text("Sin gastos registrados", color=COLOR_SUBTEXTO, italic=True)]
        page.update()

    def guardar_gasto(e):
        if not gasto_desc.value or not gasto_monto.value:
            snack("⚠️ Completa descripción y monto", COLOR_ROJO)
            return
        crear_gasto({
            "categoria":   gasto_categoria.value,
            "descripcion": gasto_desc.value,
            "monto":       float(gasto_monto.value),
            "fecha":       str(hoy),
        })
        gasto_desc.value = ""
        gasto_monto.value = ""
        cargar_gastos()
        cargar_margen()
        snack("✅ Gasto registrado")

    gastos_tab = card(
        ft.Column(
            controls=[
                ft.Text("🧾 Gastos del Negocio", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                # UX FIX: wrap=True para pantallas pequeñas
                ft.Row([gasto_categoria, gasto_desc, gasto_monto], spacing=10, wrap=True),
                ft.ElevatedButton("➕ Registrar Gasto", height=48, bgcolor="#e67e22", color="white", on_click=guardar_gasto),
                ft.Divider(),
                gastos_list,
            ],
            spacing=12,
        )
    )

    # ════════════════════ TAB 4: MERMA ═══════════════════
    merma_list = ft.Column(spacing=8)
    productos_disp = get_productos(include_sin_stock=True)
    
    # UX FIX: anchos fijos
    merma_producto = ft.Dropdown(
        label="Producto", width=220,
        options=[ft.dropdown.Option(str(p["id"]), p["nombre"]) for p in productos_disp])
    merma_cantidad = ft.TextField(label="Cantidad", width=120, keyboard_type=ft.KeyboardType.NUMBER)
    merma_motivo = ft.TextField(label="Motivo", hint_text="Caducado, dañado...", width=220)

    def cargar_mermas():
        d, h = rango()
        mermas = get_mermas(d, h)
        if mermas:
            merma_list.controls = [
                ft.Container(
                    bgcolor=COLOR_FONDO, border_radius=8, padding=12,
                    content=ft.Row([
                        ft.Text(m.get("producto_nombre", "—"), expand=True, size=13),
                        ft.Text(f"x{m['cantidad']}", size=12, color=COLOR_SUBTEXTO, width=50),
                        ft.Text(m.get("motivo", ""), size=12, color=COLOR_SUBTEXTO, width=120, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"${m['costo_total']:.2f}", weight=ft.FontWeight.BOLD, color=COLOR_ROJO, size=13),
                    ], spacing=8),
                ) for m in mermas
            ]
        else:
            merma_list.controls = [ft.Text("Sin pérdidas registradas", color=COLOR_SUBTEXTO, italic=True)]
        page.update()

    def guardar_merma(e):
        if not merma_producto.value or not merma_cantidad.value or not merma_motivo.value:
            snack("⚠️ Completa todos los campos", COLOR_ROJO)
            return
        crear_merma({
            "producto_id": merma_producto.value,
            "cantidad":    float(merma_cantidad.value),
            "motivo":      merma_motivo.value,
            "fecha":       str(hoy),
        })
        merma_cantidad.value = ""
        merma_motivo.value = ""
        cargar_mermas()
        cargar_margen()
        snack("✅ Merma registrada")

    merma_tab = card(
        ft.Column(
            controls=[
                ft.Text("📉 Merma y Pérdidas", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                # UX FIX: Formularios Responsivos
                ft.Row([merma_producto, merma_cantidad, merma_motivo], spacing=10, wrap=True),
                ft.ElevatedButton("➕ Registrar Pérdida", height=48, bgcolor=COLOR_ROJO, color="white", on_click=guardar_merma),
                ft.Divider(),
                merma_list,
            ],
            spacing=12,
        )
    )

    # ════════════════ TAB 5: COMPARATIVAS ═════════════════
    comparativa_content = ft.Column(spacing=8)
    periodo = ft.Dropdown(
        label="Período", value="semanal", width=180,
        options=[
            ft.dropdown.Option("semanal", "Últimos 7 días"),
            ft.dropdown.Option("mensual", "Este mes"),
            ft.dropdown.Option("anual",   "Este año"),
        ],
    )

    def cargar_comparativa():
        data = get_comparativa(periodo.value)
        if not data:
            comparativa_content.controls = [
                ft.Text("Sin datos suficientes", color=COLOR_SUBTEXTO, italic=True)
            ]
            page.update()
            return

        titulos = {
            "semanal": "Ventas - Últimos 7 días",
            "mensual": "Ventas - Este mes",
            "anual": "Ventas - Este año",
        }
        img_base64 = grafica_barras_comparativa(data, titulos.get(periodo.value, ""))

        if img_base64:
            comparativa_content.controls = [
                ft.Image(src_base64=img_base64, fit=ft.ImageFit.CONTAIN, expand=True)
            ]
        else:
            comparativa_content.controls = [
                ft.Text("Sin datos para graficar", color=COLOR_SUBTEXTO, italic=True)
            ]
        page.update()

    comparativas_tab = card(
        ft.Column(
            controls=[
                ft.Text("📊 Comparativas de Ventas", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Row([
                    periodo,
                    ft.ElevatedButton("🔄 Actualizar", height=48, bgcolor=COLOR_AZUL, color="white", on_click=lambda e: cargar_comparativa()),
                ], spacing=12, wrap=True),
                ft.Divider(),
                ft.Container(
                    content=comparativa_content,
                    bgcolor=COLOR_FONDO, border_radius=12, padding=20, expand=True,
                ),
            ],
            spacing=14,
        )
    )

    # ════════════════ TAB 6: PRODUCTOS TOP ════════════════
    top_tabla = ft.Column(spacing=6)
    top_grafica = ft.Container(
        alignment=ft.alignment.center,
        bgcolor=COLOR_FONDO, border_radius=12, padding=16,
    )
    top_cantidad = ft.Dropdown(
        label="Mostrar top", value="10", width=140,
        options=[
            ft.dropdown.Option("5", "Top 5"),
            ft.dropdown.Option("10", "Top 10"),
            ft.dropdown.Option("20", "Top 20"),
        ],
    )

    def cargar_productos_top():
        d, h = rango()
        limite = int(top_cantidad.value or 10)
        productos = get_productos_mas_vendidos(d, h, limite)

        if not productos:
            top_tabla.controls = [
                ft.Text("Sin ventas registradas en este rango", color=COLOR_SUBTEXTO, italic=True)
            ]
            top_grafica.content = ft.Text(
                "Sin datos para graficar", color=COLOR_SUBTEXTO, italic=True
            )
            page.update()
            return

        filas = [
            ft.Row(
                controls=[
                    ft.Text(f"#{i + 1}", size=12, color=COLOR_SUBTEXTO, width=30),
                    ft.Text(p["producto_nombre"], size=13, color=COLOR_TEXTO,
                             weight=ft.FontWeight.BOLD, expand=True,
                             max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{p['cantidad']:.0f} uds", size=12, color=COLOR_AZUL, width=80,
                             text_align=ft.TextAlign.RIGHT),
                    ft.Text(f"${p['ingresos']:.2f}", size=13, color=COLOR_ACENTO,
                             weight=ft.FontWeight.BOLD, width=90, text_align=ft.TextAlign.RIGHT),
                ],
                spacing=8,
            )
            for i, p in enumerate(productos)
        ]
        top_tabla.controls = [
            ft.Row(
                controls=[
                    ft.Text("#", size=11, color=COLOR_SUBTEXTO, width=30),
                    ft.Text("Producto", size=11, color=COLOR_SUBTEXTO, weight=ft.FontWeight.BOLD, expand=True),
                    ft.Text("Cantidad", size=11, color=COLOR_SUBTEXTO, width=80, text_align=ft.TextAlign.RIGHT),
                    ft.Text("Ingresos", size=11, color=COLOR_SUBTEXTO, width=90, text_align=ft.TextAlign.RIGHT),
                ],
                spacing=8,
            ),
            ft.Divider(height=1),
            *filas,
        ]

        img_base64 = grafica_productos_top(productos)
        if img_base64:
            top_grafica.content = ft.Image(
                src_base64=img_base64,
                fit=ft.ImageFit.CONTAIN,
                expand=True,
            )
        else:
            top_grafica.content = ft.Text("Sin datos para graficar", color=COLOR_SUBTEXTO, italic=True)

        page.update()

    productos_top_tab = card(
        ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("🏆 Productos Más Vendidos", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Row([
                    top_cantidad,
                    ft.ElevatedButton("🔄 Actualizar", height=48, bgcolor=COLOR_ACENTO, color="white",
                                       on_click=lambda e: cargar_productos_top()),
                ], spacing=12, wrap=True),
                ft.Divider(),
                top_grafica,
                ft.Divider(),
                ft.Text("Detalle", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                top_tabla,
            ],
            spacing=14,
        )
    )

    # ── Función para refrescar todo junto ─────────────────
    def cargar_todo():
        cargar_ventas()
        cargar_margen()
        cargar_gastos()
        cargar_mermas()
        cargar_comparativa()
        cargar_productos_top()

    # ── Carga inicial ──────────────────────────────────────
    cargar_todo()

    return ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Text("📊 Reportes", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Container(
                    expand=True,
                    content=ft.Tabs(
                        selected_index=0,
                        animation_duration=250,
                        expand=True,
                        tabs=[
                            ft.Tab(text="Ventas", content=ventas_tab),
                            ft.Tab(text="Margen", content=margen_tab),
                            ft.Tab(text="Productos Top", content=productos_top_tab),
                            ft.Tab(text="Gastos", content=gastos_tab),
                            ft.Tab(text="Merma", content=merma_tab),
                            ft.Tab(text="Comparativas", content=comparativas_tab),
                        ],
                    )
                ),
            ],
        )
    )
# views/reportes_view.py
import flet as ft
from datetime import date

from database.db_manager import (
    get_reporte_ventas, get_reporte_margen,
    get_gastos, crear_gasto,
    get_mermas, crear_merma,
    get_comparativa, get_cortes_caja,
    get_productos,
)

CATEGORIAS_GASTO = ["Insumos", "Renta", "Servicios",
                    "Personal", "Otros"]

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
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto, color="white"),
            bgcolor=color)
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

    desde = ft.TextField(label="Desde", value=str(hoy),
                         height=48, expand=True)
    hasta = ft.TextField(label="Hasta", value=str(hoy),
                         height=48, expand=True)

    def rango():
        return desde.value, hasta.value

    # ════════════════════ TAB 1: VENTAS ═══════════════════
    ventas_stats = ft.Row(spacing=12, wrap=True)
    cortes_list  = ft.Column(spacing=8,
                              scroll=ft.ScrollMode.AUTO,
                              expand=True)

    def stat_box(icono, label, valor, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icono, size=20),
                    ft.Text(valor, size=18,
                            weight=ft.FontWeight.BOLD,
                            color=color),
                    ft.Text(label, size=11,
                            color=COLOR_SUBTEXTO),
                ],
                spacing=2
            ),
            bgcolor=COLOR_FONDO,
            border_radius=10,
            padding=14,
            expand=True,
        )

    def cargar_ventas():
        d, h = rango()
        data = get_reporte_ventas(d, h)
        cortes = get_cortes_caja(d, h)

        ventas_stats.controls = [
            stat_box("💰", "Ingresos",
                    f"${data.get('ingresos', 0):.2f}",
                    COLOR_ACENTO),
            stat_box("🧾", "Ventas",
                    str(data.get('cantidad_ventas', 0)),
                    COLOR_AZUL),
            stat_box("💵", "Efectivo",
                    f"${data.get('efectivo', 0):.2f}",
                    COLOR_TEXTO),
            stat_box("💳", "Tarjeta",
                    f"${data.get('tarjeta', 0):.2f}",
                    COLOR_TEXTO),
        ]

        if cortes:
            cortes_list.controls = [
                ft.Container(
                    bgcolor=COLOR_FONDO,
                    border_radius=8,
                    padding=12,
                    content=ft.Row(
                        controls=[
                            ft.Text(str(c["fecha"]),
                                    expand=True, size=13),
                            ft.Text(f"🧾 {c['total_ventas']}",
                                    size=12,
                                    color=COLOR_SUBTEXTO,
                                    width=70),
                            ft.Text(f"${c['total_ingresos']:.2f}",
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                    color=COLOR_ACENTO),
                        ],
                    ),
                )
                for c in cortes
            ]
        else:
            cortes_list.controls = [
                ft.Text("Sin cortes de caja en este rango",
                        color=COLOR_SUBTEXTO, italic=True)
            ]
        page.update()

    ventas_tab = card(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("📊 Ventas y Cortes de Caja", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ft.Row([desde, hasta,
                       ft.ElevatedButton(
                           "🔄 Actualizar", height=48,
                           bgcolor=COLOR_ACENTO, color="white",
                           on_click=lambda e: cargar_todo())
                       ], spacing=12),
                ventas_stats,
                ft.Divider(),
                ft.Text("Historial de Cortes de Caja", size=14,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
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
        color_ganancia = COLOR_ACENTO if ganancia >= 0 \
            else COLOR_ROJO

        margen_content.controls = [
            ft.Row([
                stat_box("💰", "Ingresos",
                        f"${data.get('ingresos', 0):.2f}",
                        COLOR_AZUL),
                stat_box("📦", "Costo Productos",
                        f"${data.get('costo_productos', 0):.2f}",
                        COLOR_TEXTO),
            ], spacing=12),
            ft.Row([
                stat_box("🧾", "Gastos",
                        f"${data.get('gastos', 0):.2f}",
                        "#e67e22"),
                stat_box("📉", "Merma",
                        f"${data.get('merma', 0):.2f}",
                        COLOR_ROJO),
            ], spacing=12),
            ft.Divider(),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Ganancia Neta", size=14,
                                color=COLOR_SUBTEXTO),
                        ft.Text(f"${ganancia:.2f}", size=32,
                                weight=ft.FontWeight.BOLD,
                                color=color_ganancia),
                        ft.Text(
                            f"Margen: {data.get('margen_pct', 0):.1f}%",
                            size=14, color=COLOR_SUBTEXTO),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=COLOR_FONDO,
                border_radius=12,
                padding=20,
                alignment=ft.alignment.center,
            )
        ]
        page.update()

    margen_tab = card(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("📈 Margen Real de Ganancia", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ft.Text(
                    "Ingresos - Costos - Gastos - Merma",
                    size=12, color=COLOR_SUBTEXTO),
                margen_content,
            ],
            spacing=14,
        )
    )

    # ════════════════════ TAB 3: GASTOS ═══════════════════
    gastos_list = ft.Column(spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                            expand=True)
    gasto_categoria = ft.Dropdown(
        label="Categoría", value="Insumos", height=48,
        options=[ft.dropdown.Option(c)
                for c in CATEGORIAS_GASTO])
    gasto_desc  = ft.TextField(label="Descripción",
                               height=48, expand=True)
    gasto_monto = ft.TextField(label="Monto", prefix_text="$",
                               height=48, width=140,
                               keyboard_type=ft.KeyboardType.NUMBER)

    def cargar_gastos():
        d, h = rango()
        gastos = get_gastos(d, h)
        if gastos:
            gastos_list.controls = [
                ft.Container(
                    bgcolor=COLOR_FONDO,
                    border_radius=8,
                    padding=12,
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(g["categoria"],
                                           size=11, color="white"),
                            bgcolor="#e67e22",
                            border_radius=6,
                            padding=ft.padding.symmetric(
                                horizontal=8, vertical=4)
                        ),
                        ft.Text(g["descripcion"], expand=True,
                                size=13),
                        ft.Text(f"${g['monto']:.2f}",
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_ROJO, size=13),
                    ], spacing=10),
                )
                for g in gastos
            ]
        else:
            gastos_list.controls = [
                ft.Text("Sin gastos registrados",
                        color=COLOR_SUBTEXTO, italic=True)
            ]
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
            expand=True,
            controls=[
                ft.Text("🧾 Gastos del Negocio", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ft.Row([gasto_categoria, gasto_desc,
                       gasto_monto], spacing=10),
                ft.ElevatedButton(
                    "➕ Registrar Gasto", height=48,
                    bgcolor="#e67e22", color="white",
                    on_click=guardar_gasto),
                ft.Divider(),
                gastos_list,
            ],
            spacing=12,
        )
    )

    # ════════════════════ TAB 4: MERMA ═══════════════════
    merma_list = ft.Column(spacing=8,
                           scroll=ft.ScrollMode.AUTO,
                           expand=True)
    productos_disp = get_productos()
    merma_producto = ft.Dropdown(
        label="Producto", height=48, expand=True,
        options=[ft.dropdown.Option(str(p["id"]), p["nombre"])
                for p in productos_disp])
    merma_cantidad = ft.TextField(label="Cantidad", height=48,
                                  width=110,
                                  keyboard_type=ft.KeyboardType.NUMBER)
    merma_motivo = ft.TextField(label="Motivo",
                                hint_text="Caducado, dañado...",
                                height=48, expand=True)

    def cargar_mermas():
        d, h = rango()
        mermas = get_mermas(d, h)
        if mermas:
            merma_list.controls = [
                ft.Container(
                    bgcolor=COLOR_FONDO,
                    border_radius=8,
                    padding=12,
                    content=ft.Row([
                        ft.Text(m.get("producto_nombre", "—"),
                                expand=True, size=13),
                        ft.Text(f"x{m['cantidad']}",
                                size=12, color=COLOR_SUBTEXTO,
                                width=50),
                        ft.Text(m.get("motivo", ""), size=12,
                                color=COLOR_SUBTEXTO,
                                width=120,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"${m['costo_total']:.2f}",
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_ROJO, size=13),
                    ], spacing=8),
                )
                for m in mermas
            ]
        else:
            merma_list.controls = [
                ft.Text("Sin pérdidas registradas",
                        color=COLOR_SUBTEXTO, italic=True)
            ]
        page.update()

    def guardar_merma(e):
        if not merma_producto.value or not merma_cantidad.value \
           or not merma_motivo.value:
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
            expand=True,
            controls=[
                ft.Text("📉 Merma y Pérdidas", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ft.Row([merma_producto, merma_cantidad],
                      spacing=10),
                merma_motivo,
                ft.ElevatedButton(
                    "➕ Registrar Pérdida", height=48,
                    bgcolor=COLOR_ROJO, color="white",
                    on_click=guardar_merma),
                ft.Divider(),
                merma_list,
            ],
            spacing=12,
        )
    )

    # ════════════════ TAB 5: COMPARATIVAS ═════════════════
    comparativa_content = ft.Column(spacing=8)
    periodo = ft.Dropdown(
        label="Período", value="semanal", height=48,
        width=180,
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
                ft.Text("Sin datos suficientes",
                        color=COLOR_SUBTEXTO, italic=True)
            ]
            page.update()
            return

        max_val = max((float(d["total"]) for d in data),
                      default=1) or 1

        barras = []
        for item in data:
            altura = max(
                10, (float(item["total"]) / max_val) * 150)
            barras.append(
                ft.Column(
                    controls=[
                        ft.Text(f"${float(item['total']):.0f}",
                                size=10, color=COLOR_TEXTO),
                        ft.Container(
                            height=altura, width=30,
                            bgcolor=COLOR_ACENTO,
                            border_radius=4,
                        ),
                        ft.Text(str(item["grupo"]), size=10,
                                color=COLOR_SUBTEXTO),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4
                )
            )

        comparativa_content.controls = [
            ft.Row(
                controls=barras,
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                vertical_alignment=ft.CrossAxisAlignment.END,
            )
        ]
        page.update()

    comparativas_tab = card(
        ft.Column(
            expand=True,
            controls=[
                ft.Text("📊 Comparativas de Ventas", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ft.Row([
                    periodo,
                    ft.ElevatedButton(
                        "🔄 Actualizar", height=48,
                        bgcolor=COLOR_AZUL, color="white",
                        on_click=lambda e: cargar_comparativa()),
                ], spacing=12),
                ft.Divider(),
                ft.Container(
                    content=comparativa_content,
                    bgcolor=COLOR_FONDO,
                    border_radius=12,
                    padding=20,
                    expand=True,
                ),
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

    # ── Carga inicial ──────────────────────────────────────
    cargar_ventas()
    cargar_margen()
    cargar_gastos()
    cargar_mermas()
    cargar_comparativa()

    return ft.Column(
        expand=True,
        spacing=12,
        controls=[
            ft.Text("📊 Reportes", size=22,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_TEXTO),
            ft.Tabs(
                selected_index=0,
                animation_duration=250,
                expand=True,
                tabs=[
                    ft.Tab(text="Ventas", content=ventas_tab),
                    ft.Tab(text="Margen", content=margen_tab),
                    ft.Tab(text="Gastos", content=gastos_tab),
                    ft.Tab(text="Merma", content=merma_tab),
                    ft.Tab(text="Comparativas",
                          content=comparativas_tab),
                ],
            ),
        ],
    )
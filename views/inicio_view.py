import flet as ft
from database.db_manager import get_resumen_dia

COLOR_TEXTO    = "#2c3e50"
COLOR_SUBTEXTO = "#7f8c8d"
COLOR_TARJETA  = "#ffffff"
COLOR_ACENTO   = "#00b894"
COLOR_NARANJA  = "#ff7a00"
COLOR_AZUL     = "#3498db"
COLOR_ROJO     = "#e74c3c"
COLOR_FONDO    = "#f0f4f8"

def inicio_view(page: ft.Page, on_cambiar=None):

    def navegar(modulo):
        if on_cambiar:
            on_cambiar(modulo)

    resumen = get_resumen_dia()

    # Extracción de métricas financieras
    efectivo = resumen.get('efectivo', 0)
    tarjeta = resumen.get('tarjeta', 0)
    total_ingresos = efectivo + tarjeta

    # Cálculo seguro de porcentajes para evitar división por cero
    pct_efectivo = (efectivo / total_ingresos * 100) if total_ingresos > 0 else 0
    pct_tarjeta = (tarjeta / total_ingresos * 100) if total_ingresos > 0 else 0

    def tarjeta_stat(icono, titulo, valor, color, subtitulo="", modulo=None):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icono, size=28),
                    ft.Text(str(valor), size=28, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(titulo, size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                    ft.Text(subtitulo, size=11, color=COLOR_SUBTEXTO),
                ],
                spacing=4
            ),
            bgcolor=COLOR_TARJETA,
            border_radius=14,
            padding=20,
            expand=True,
            on_click=lambda e, m=modulo: navegar(m) if m else None,
            shadow=ft.BoxShadow(blur_radius=8, color="#00000015", offset=ft.Offset(0, 2))
        )

    def acceso_rapido(icono, titulo, subtitulo, color, modulo):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icono, size=32),
                    ft.Text(titulo, size=14, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(subtitulo, size=11, color="#ffffff80"),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=color,
            border_radius=14,
            padding=20,
            expand=True,
            alignment=ft.Alignment(0, 0),
            on_click=lambda e, m=modulo: navegar(m),
        )

    def barra_ingreso(titulo, monto, porcentaje, color):
        ancho = max(1, porcentaje)
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(titulo, size=12, color=COLOR_TEXTO, weight=ft.FontWeight.BOLD),
                        ft.Text(f"${monto:.2f} - {porcentaje:.1f}%", size=12, color=COLOR_SUBTEXTO),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(bgcolor=color, height=12, width=ancho * 2.4, border_radius=6),
                        ]
                    ),
                    bgcolor="#eef2f5",
                    border_radius=6,
                    height=12,
                    width=240,
                ),
            ],
            spacing=6,
        )

    grafica_ingresos = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Distribucion de Ingresos", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                ft.Divider(),
                ft.Container(height=14),
                barra_ingreso("Efectivo", efectivo, pct_efectivo, COLOR_ACENTO),
                ft.Container(height=10),
                barra_ingreso("Tarjeta", tarjeta, pct_tarjeta, COLOR_AZUL),
            ],
            spacing=8,
        ),
        bgcolor=COLOR_TARJETA,
        border_radius=14,
        padding=20,
        expand=True,
        shadow=ft.BoxShadow(blur_radius=8, color="#00000015", offset=ft.Offset(0, 2))
    )
    return ft.Column(
        controls=[
            ft.Text("Dashboard Operativo", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
            ft.Text("Métricas financieras en tiempo real", size=13, color=COLOR_SUBTEXTO),
            ft.Container(height=8),
            
            # Fila 1: KPIs
            ft.Row(
                controls=[
                    tarjeta_stat("💰", "Ventas Hoy", f"${resumen.get('total', 0):.2f}", COLOR_ACENTO, f"{resumen.get('total_ventas', 0)} transacciones", "ventas"),
                    tarjeta_stat("📦", "Productos Activos", resumen.get("productos_activos", 0), COLOR_AZUL, "en el catálogo", "productos"),
                    tarjeta_stat("⚠️", "Stock Crítico", resumen.get("stock_bajo", 0), COLOR_ROJO, "productos con ≤5 unidades", "productos"),
                ],
                spacing=16
            ),
            
            ft.Container(height=20),
            
            # Fila 2: Gráfica y Accesos Rápidos
            ft.Row(
                controls=[
                    # Panel Izquierdo: Gráfica
                    grafica_ingresos,
                    
                    # Panel Derecho: Botones de Acción
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Accesos Rápidos", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                                ft.Row([
                                    acceso_rapido("🛒", "Nueva Venta", "Iniciar transacción", COLOR_ACENTO, "ventas"),
                                    acceso_rapido("📦", "Productos", "Gestión de inventario", COLOR_AZUL, "productos"),
                                ], spacing=12, expand=True),
                                ft.Row([
                                    acceso_rapido("📊", "Reportes", "Análisis histórico", COLOR_NARANJA, "reportes"),
                                    acceso_rapido("🏧", "Caja", "Arqueo de fondos", "#9b59b6", "caja"),
                                ], spacing=12, expand=True)
                            ],
                            spacing=12,
                            expand=True
                        ),
                        expand=True
                    )
                ],
                spacing=16,
                expand=True
            )
        ],
        expand=True,
        spacing=8,
        scroll=ft.ScrollMode.AUTO
    )




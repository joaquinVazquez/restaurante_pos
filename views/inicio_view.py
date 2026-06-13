# views/inicio_view.py
import flet as ft
from database.db_manager import get_resumen_dia

COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#ffffff"
COLOR_ACENTO     = "#00b894"
COLOR_NARANJA    = "#ff7a00"
COLOR_AZUL       = "#3498db"
COLOR_ROJO       = "#e74c3c"
COLOR_FONDO      = "#f0f4f8"


def inicio_view(page: ft.Page, on_cambiar=None):

    def navegar(modulo):
        if on_cambiar:
            on_cambiar(modulo)

    resumen = get_resumen_dia()

    def tarjeta_stat(icono, titulo, valor, color,
                     subtitulo="", modulo=None):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icono, size=28),
                    ft.Text(str(valor), size=28,
                            weight=ft.FontWeight.BOLD,
                            color=color),
                    ft.Text(titulo, size=13,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_TEXTO),
                    ft.Text(subtitulo, size=11,
                            color=COLOR_SUBTEXTO),
                ],
                spacing=4
            ),
            bgcolor=COLOR_TARJETA,
            border_radius=14,
            padding=20,
            expand=True,
            on_click=lambda e, m=modulo: navegar(m) if m else None,
            shadow=ft.BoxShadow(
                blur_radius=8,
                color="#00000015",
                offset=ft.Offset(0, 2)
            )
        )

    def acceso_rapido(icono, titulo, subtitulo, color, modulo):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icono, size=32),
                    ft.Text(titulo, size=14,
                            weight=ft.FontWeight.BOLD,
                            color="white"),
                    ft.Text(subtitulo, size=11,
                            color="#ffffff80"),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=color,
            border_radius=14,
            padding=20,
            expand=True,
            alignment=ft.alignment.center,
            on_click=lambda e, m=modulo: navegar(m),
        )

    return ft.Column(
        controls=[
            ft.Text("🏠 Inicio", size=22,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_TEXTO),
            ft.Text("Resumen del día", size=13,
                    color=COLOR_SUBTEXTO),
            ft.Container(height=8),
            ft.Row(
                controls=[
                    tarjeta_stat(
                        "💰", "Ventas Hoy",
                        f"${resumen.get('total', 0):.2f}",
                        COLOR_ACENTO,
                        f"{resumen.get('total_ventas', 0)} transacciones",
                        "ventas"
                    ),
                    tarjeta_stat(
                        "📦", "Productos Activos",
                        resumen.get("productos_activos", 0),
                        COLOR_AZUL,
                        "en el menú",
                        "productos"
                    ),
                    tarjeta_stat(
                        "⚠️", "Stock Bajo",
                        resumen.get("stock_bajo", 0),
                        COLOR_ROJO,
                        "productos con ≤5 unidades",
                        "productos"
                    ),
                ],
                spacing=16
            ),
            ft.Container(height=20),
            ft.Text("⚡ Accesos Rápidos", size=15,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_TEXTO),
            ft.Container(height=8),
            ft.Row(
                controls=[
                    acceso_rapido("🛒", "Nueva Venta",
                                  "Iniciar una venta",
                                  COLOR_ACENTO, "ventas"),
                    acceso_rapido("📦", "Productos",
                                  "Gestionar menú",
                                  COLOR_AZUL, "productos"),
                    acceso_rapido("📊", "Reportes",
                                  "Ver estadísticas",
                                  COLOR_NARANJA, "reportes"),
                    acceso_rapido("🏧", "Caja",
                                  "Corte de caja",
                                  "#9b59b6", "caja"),
                ],
                spacing=12
            ),
        ],
        expand=True,
        spacing=8
    )
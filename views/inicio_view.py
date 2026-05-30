# views/inicio_view.py
import flet as ft
from database.connection import execute_query

COLOR_TEXTO      = "#2c3e50"
COLOR_SUBTEXTO   = "#7f8c8d"
COLOR_TARJETA    = "#ffffff"
COLOR_ACENTO     = "#00b894"
COLOR_NARANJA    = "#ff7a00"
COLOR_AZUL       = "#3498db"
COLOR_ROJO       = "#e74c3c"
COLOR_FONDO      = "#f0f4f8"


def inicio_view(page: ft.Page, on_cambiar=None):

    def get_stats():
        try:
            ventas_hoy = execute_query("""
                SELECT COALESCE(SUM(total), 0) AS total,
                       COUNT(*) AS cantidad
                FROM ventas
                WHERE DATE(creado_en) = CURRENT_DATE
            """)
            productos = execute_query(
                "SELECT COUNT(*) AS total FROM productos WHERE activo = TRUE"
            )
            stock_bajo = execute_query(
                "SELECT COUNT(*) AS total FROM productos WHERE stock <= 5 AND activo = TRUE"
            )
            return ventas_hoy[0], productos[0], stock_bajo[0]
        except:
            return {"total": 0, "cantidad": 0}, {"total": 0}, {"total": 0}

    ventas_hoy, productos, stock_bajo = get_stats()

    def navegar(modulo):
        if on_cambiar:
            on_cambiar(modulo)

    def tarjeta_stat(icono, titulo, valor, color, subtitulo=""):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[ft.Text(icono, size=28)]),
                    ft.Text(str(valor), size=28,
                            weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(titulo, size=13,
                            weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
                    ft.Text(subtitulo, size=11, color=COLOR_SUBTEXTO),
                ],
                spacing=4
            ),
            bgcolor=COLOR_TARJETA,
            border_radius=14,
            padding=20,
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=8,
                color="#00000015",
                offset=ft.Offset(0, 2)
            ),
            on_click=lambda e: navegar("ventas")
            if titulo == "Ventas Hoy" else None
        )

    return ft.Column(
        controls=[
            ft.Text("🏠 Inicio", size=22,
                    weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
            ft.Text("Resumen del día", size=13, color=COLOR_SUBTEXTO),
            ft.Container(height=8),
            # Tarjetas estadísticas
            ft.Row(
                controls=[
                    tarjeta_stat(
                        "💰", "Ventas Hoy",
                        f"${ventas_hoy['total']:.2f}",
                        COLOR_ACENTO,
                        f"{ventas_hoy['cantidad']} transacciones"
                    ),
                    tarjeta_stat(
                        "📦", "Productos Activos",
                        productos["total"],
                        COLOR_AZUL,
                        "en el menú"
                    ),
                    tarjeta_stat(
                        "⚠️", "Stock Bajo",
                        stock_bajo["total"],
                        COLOR_ROJO,
                        "productos con ≤5 unidades"
                    ),
                ],
                spacing=16
            ),
            ft.Container(height=20),
            ft.Text("⚡ Accesos Rápidos", size=15,
                    weight=ft.FontWeight.BOLD, color=COLOR_TEXTO),
            ft.Container(height=8),
            # Accesos rápidos
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("🛒", size=32),
                                ft.Text("Nueva Venta", size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color="white"),
                                ft.Text("Iniciar una venta",
                                        size=11, color="#ffffff80"),
                            ],
                            spacing=4,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        bgcolor=COLOR_ACENTO,
                        border_radius=14,
                        padding=20,
                        expand=True,
                        alignment=ft.alignment.center,
                        on_click=lambda e: navegar("ventas"),
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("📦", size=32),
                                ft.Text("Productos", size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color="white"),
                                ft.Text("Gestionar menú",
                                        size=11, color="#ffffff80"),
                            ],
                            spacing=4,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        bgcolor=COLOR_AZUL,
                        border_radius=14,
                        padding=20,
                        expand=True,
                        alignment=ft.alignment.center,
                        on_click=lambda e: navegar("productos"),
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("📊", size=32),
                                ft.Text("Reportes", size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color="white"),
                                ft.Text("Ver estadísticas",
                                        size=11, color="#ffffff80"),
                            ],
                            spacing=4,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        bgcolor=COLOR_NARANJA,
                        border_radius=14,
                        padding=20,
                        expand=True,
                        alignment=ft.alignment.center,
                        on_click=lambda e: navegar("reportes"),
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("🏧", size=32),
                                ft.Text("Caja", size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color="white"),
                                ft.Text("Corte de caja",
                                        size=11, color="#ffffff80"),
                            ],
                            spacing=4,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        bgcolor="#9b59b6",
                        border_radius=14,
                        padding=20,
                        expand=True,
                        alignment=ft.alignment.center,
                        on_click=lambda e: navegar("caja"),
                    ),
                ],
                spacing=12
            ),
        ],
        expand=True,
        spacing=8
    )
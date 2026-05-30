# views/sidebar.py
import flet as ft

COLOR_SIDEBAR    = "#1a1f2e"
COLOR_ACTIVO     = "#00b894"
COLOR_TEXTO      = "#ffffff"
COLOR_SUBTEXTO   = "#a0aec0"
COLOR_HOVER      = "#2d3748"

def sidebar(page: ft.Page, modulo_activo: str, on_cambiar):
    """
    Sidebar de navegación estilo Pulpos.
    on_cambiar(modulo) — callback cuando el usuario cambia de módulo.
    """

    def item_menu(icono, texto, modulo):
        activo = modulo == modulo_activo
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(icono, size=18),
                    ft.Text(
                        texto,
                        size=13,
                        color=COLOR_TEXTO if activo else COLOR_SUBTEXTO,
                        weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL
                    )
                ],
                spacing=12
            ),
            bgcolor=COLOR_ACTIVO if activo else "transparent",
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            on_click=lambda e, m=modulo: on_cambiar(m),
            on_hover=lambda e: setattr(e.control, 'bgcolor',
                COLOR_ACTIVO if modulo == modulo_activo else
                (COLOR_HOVER if e.data == "true" else "transparent")
            ) or page.update(),
        )

    btn_nueva_venta = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("＋", size=18, color="white"),
                ft.Text("Nueva Venta", size=13,
                        color="white", weight=ft.FontWeight.BOLD)
            ],
            spacing=10
        ),
        bgcolor="#00b894",
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=14, vertical=12),
        on_click=lambda e: on_cambiar("ventas"),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                # Logo
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("🍽️", size=24),
                            ft.Text("RestaurantePOS",
                                    size=14,
                                    color=COLOR_TEXTO,
                                    weight=ft.FontWeight.BOLD)
                        ],
                        spacing=8
                    ),
                    padding=ft.padding.only(bottom=20)
                ),
                # Botón Nueva Venta
                btn_nueva_venta,
                ft.Container(height=16),
                # Menú
                item_menu("🏠", "Inicio",     "inicio"),
                item_menu("📦", "Productos",  "productos"),
                item_menu("💰", "Ventas",     "ventas"),
                item_menu("📊", "Reportes",   "reportes"),
                item_menu("🏧", "Caja",       "caja"),
                item_menu("👥", "Clientes",   "clientes"),
                item_menu("⚙️", "Configuración", "config"),
                ft.Container(expand=True),
                # Usuario
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                content=ft.Text("A", color="white", size=12),
                                bgcolor="#00b894",
                                radius=16
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("Admin", size=12,
                                            color=COLOR_TEXTO,
                                            weight=ft.FontWeight.BOLD),
                                    ft.Text("Administrador", size=10,
                                            color=COLOR_SUBTEXTO)
                                ],
                                spacing=2
                            )
                        ],
                        spacing=10
                    ),
                    padding=ft.padding.only(top=10)
                )
            ],
            expand=True,
            spacing=4
        ),
        bgcolor=COLOR_SIDEBAR,
        width=200,
        padding=16,
        expand=False
    )
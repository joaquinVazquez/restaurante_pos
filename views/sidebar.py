# views/sidebar.py
import flet as ft

COLOR_SIDEBAR  = "#1a1f2e"
COLOR_ACTIVO   = "#00b894"
COLOR_TEXTO    = "#ffffff"
COLOR_SUBTEXTO = "#a0aec0"

MENU_ITEMS = [
    ("🏠", "Inicio",        "inicio"),
    ("📦", "Productos",     "productos"),
    ("💰", "Ventas",        "ventas"),
    ("📊", "Reportes",      "reportes"),
    ("🏧", "Caja",          "caja"),
    ("👥", "Clientes",      "clientes"),
    ("⚙️", "Configuración", "config"),
]


def sidebar(page: ft.Page, modulo_activo: str,
            on_cambiar, usuario=None,
            on_cerrar_sesion=None,
            modulos_permitidos=None):

    if modulos_permitidos is None:
        modulos_permitidos = [m[2] for m in MENU_ITEMS]

    def item_menu(icono, texto, modulo):
        if modulo not in modulos_permitidos:
            return None
        activo = modulo == modulo_activo
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(icono, size=18),
                    ft.Text(
                        texto,
                        size=13,
                        color=COLOR_TEXTO if activo
                        else COLOR_SUBTEXTO,
                        weight=ft.FontWeight.BOLD if activo
                        else ft.FontWeight.NORMAL
                    )
                ],
                spacing=12
            ),
            bgcolor=COLOR_ACTIVO if activo else "transparent",
            border_radius=10,
            padding=ft.padding.symmetric(
                horizontal=14, vertical=10),
            on_click=lambda e, m=modulo: on_cambiar(m),
        )

    nombre    = usuario["nombre"] if usuario else "Usuario"
    rol       = usuario["rol"].capitalize() if usuario else ""
    iniciales = nombre[0].upper() if nombre else "U"

    items_menu = []
    for icono, texto, modulo in MENU_ITEMS:
        item = item_menu(icono, texto, modulo)
        if item:
            items_menu.append(item)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("🍽️", size=24),
                            ft.Text(
                                "RestaurantePOS",
                                size=14,
                                color=COLOR_TEXTO,
                                weight=ft.FontWeight.BOLD
                            )
                        ],
                        spacing=8
                    ),
                    padding=ft.padding.only(bottom=20)
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("＋", size=18, color="white"),
                            ft.Text(
                                "Nueva Venta",
                                size=13,
                                color="white",
                                weight=ft.FontWeight.BOLD
                            )
                        ],
                        spacing=10
                    ),
                    bgcolor=COLOR_ACTIVO,
                    border_radius=10,
                    padding=ft.padding.symmetric(
                        horizontal=14, vertical=12),
                    on_click=lambda e: on_cambiar("ventas"),
                ),
                ft.Container(height=16),
                *items_menu,
                ft.Container(expand=True),
                ft.Divider(color="#ffffff20"),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                content=ft.Text(
                                    iniciales,
                                    color="white",
                                    size=12
                                ),
                                bgcolor=COLOR_ACTIVO,
                                radius=16
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        nombre,
                                        size=12,
                                        color=COLOR_TEXTO,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        rol,
                                        size=10,
                                        color=COLOR_SUBTEXTO
                                    )
                                ],
                                spacing=2,
                                expand=True
                            ),
                            ft.IconButton(
                                icon=ft.icons.LOGOUT,
                                icon_color=COLOR_SUBTEXTO,
                                icon_size=18,
                                tooltip="Cerrar sesión",
                                on_click=lambda e:
                                    on_cerrar_sesion()
                                    if on_cerrar_sesion else None
                            )
                        ],
                        spacing=8
                    ),
                    padding=ft.padding.only(top=8)
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
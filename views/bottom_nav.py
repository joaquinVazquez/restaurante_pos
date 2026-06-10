# views/bottom_nav.py
import flet as ft

COLOR_BG     = "#1a1f2e"
COLOR_ACTIVO = "#00b894"
COLOR_TEXTO  = "#ffffff"
COLOR_MUTED  = "#a0aec0"

ITEMS = {
    "inicio":    ("🏠", "Inicio"),
    "ventas":    ("💰", "Ventas"),
    "productos": ("📦", "Productos"),
    "reportes":  ("📊", "Reportes"),
    "caja":      ("🏧", "Caja"),
    "clientes":  ("👥", "Clientes"),
    "config":    ("⚙️", "Config"),
}


def bottom_nav(page: ft.Page, modulo_activo: str,
               modulos_visibles: list, on_cambiar):

    def nav_item(modulo: str):
        icono, label = ITEMS.get(modulo, ("●", modulo))
        activo = modulo == modulo_activo

        return ft.Container(
            expand=True,
            height=64,
            ink=True,
            on_click=lambda e, m=modulo: on_cambiar(m),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    ft.Text(
                        icono,
                        size=20,
                        color=COLOR_ACTIVO if activo
                        else COLOR_MUTED,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        label,
                        size=11,
                        color=COLOR_TEXTO if activo
                        else COLOR_MUTED,
                        weight=ft.FontWeight.BOLD if activo
                        else ft.FontWeight.NORMAL,
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
            ),
        )

    return ft.Container(
        height=72,
        bgcolor=COLOR_BG,
        padding=ft.padding.symmetric(horizontal=4, vertical=4),
        shadow=ft.BoxShadow(
            blur_radius=8,
            color="#00000030",
            offset=ft.Offset(0, -2)
        ),
        content=ft.Row(
            controls=[nav_item(m) for m in modulos_visibles],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
    )
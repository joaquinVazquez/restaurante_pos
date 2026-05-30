# main.py
import flet as ft
from views.sidebar import sidebar
from views.ventas_view import ventas_view
from views.inicio_view import inicio_view
from views.productos_view import productos_view
from views.reportes_view import reportes_view
from views.caja_view import caja_view
from views.clientes_view import clientes_view

COLOR_FONDO = "#f0f4f8"

def main(page: ft.Page):
    page.title      = "🍽️  RestaurantePOS"
    page.bgcolor    = COLOR_FONDO
    page.padding    = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    modulo_actual = {"valor": "inicio"}

    area_contenido = ft.Container(
        expand=True,
        padding=24,
        bgcolor=COLOR_FONDO
    )

    def cargar_modulo(modulo):
        modulo_actual["valor"] = modulo

        if modulo == "inicio":
            contenido = inicio_view(page, on_cambiar=cargar_modulo)
        elif modulo == "ventas":
            contenido = ventas_view(page)
        elif modulo == "productos":
            contenido = productos_view(page)
        elif modulo == "reportes":
            contenido = reportes_view(page)
        elif modulo == "caja":
            contenido = caja_view(page)
        elif modulo == "clientes":
            contenido = clientes_view(page)
        else:
            contenido = ft.Column(
                controls=[
                    ft.Text(f"Módulo: {modulo}", size=22,
                            weight=ft.FontWeight.BOLD),
                    ft.Text("Próximamente...", size=14),
                ],
                expand=True
            )

        area_contenido.content = contenido
        layout.controls[0] = sidebar(page, modulo, cargar_modulo)
        page.update()

    layout = ft.Row(
        controls=[
            sidebar(page, "inicio", cargar_modulo),
            area_contenido
        ],
        expand=True,
        spacing=0
    )

    area_contenido.content = inicio_view(page, on_cambiar=cargar_modulo)
    page.add(layout)
    page.update()

ft.app(target=main)
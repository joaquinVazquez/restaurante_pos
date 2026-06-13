# main.py
import flet as ft
from database.init_db import inicializar_bd
from controllers.auth_controller import (
    cerrar_sesion, get_modulos_permitidos
)
from views.login_view import login_view
from views.sidebar import sidebar
from views.bottom_nav import bottom_nav
from views.ventas_view import ventas_view
from views.inicio_view import inicio_view
from views.productos_view import productos_view
from views.reportes_view import reportes_view
from views.caja_view import caja_view
from views.clientes_view import clientes_view

COLOR_FONDO      = "#f0f4f8"
BREAKPOINT_MOVIL = 800
BOTTOM_NAV_H     = 72

inicializar_bd()
from database.db_manager import verificar_conexion
verificar_conexion()


def es_movil(page: ft.Page) -> bool:
    return page.width is not None and page.width <= BREAKPOINT_MOVIL


def main(page: ft.Page):
    page.title      = "🍽️  RestaurantePOS"
    page.bgcolor    = COLOR_FONDO
    page.padding    = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    estado = {
        "modulo":  "inicio",
        "usuario": None
    }

    area_contenido = ft.Container(
        bgcolor=COLOR_FONDO,
        expand=True
    )

    def mostrar_login():
        estado["usuario"] = None
        page.controls.clear()
        page.add(
            login_view(page, on_login_exitoso=mostrar_app)
        )
        page.update()

    def mostrar_app(usuario):
        estado["usuario"] = usuario
        cargar_modulo("inicio")

    def hacer_cerrar_sesion():
        cerrar_sesion()
        mostrar_login()

    def cargar_modulo(modulo):
        usuario = estado["usuario"]
        modulos = get_modulos_permitidos(
            usuario["rol"]) if usuario else []

        if modulo not in modulos:
            modulo = modulos[0] if modulos else "inicio"

        estado["modulo"] = modulo

        if modulo == "inicio":
            contenido = inicio_view(
                page, on_cambiar=cargar_modulo)
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
                    ft.Text(f"Módulo: {modulo}",
                            size=22,
                            weight=ft.FontWeight.BOLD),
                    ft.Text("Próximamente...", size=14),
                ],
            )

        area_contenido.content = contenido
        reconstruir_layout()

    def reconstruir_layout():
        usuario = estado["usuario"]
        if not usuario:
            return

        modulo  = estado["modulo"]
        modulos = get_modulos_permitidos(usuario["rol"])

        page.controls.clear()

        if es_movil(page):
            # ── Móvil: Stack con bottom nav fijo ──────────
           layout = ft.Stack(
                width=page.width,
                height=page.height,
                controls=[
                    # Contenido con padding inferior
                    ft.Container(
                        expand=True,
                        padding=ft.padding.only(
                            left=12,
                            right=12,
                            top=12,
                            bottom=BOTTOM_NAV_H + 12
                        ),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=area_contenido,
                    ),
                    # Bottom nav pegado al fondo
                    ft.Container(
                        left=0,
                        right=0,
                        bottom=0,
                        height=BOTTOM_NAV_H,
                        content=bottom_nav(
                            page=page,
                            modulo_activo=modulo,
                            modulos_visibles=modulos,
                            on_cambiar=cargar_modulo
                        ),
                    ),
                ]
            )
        else:
            # ── Desktop: sidebar + contenido ──────────────
            layout = ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    sidebar(
                        page=page,
                        modulo_activo=modulo,
                        on_cambiar=cargar_modulo,
                        usuario=usuario,
                        on_cerrar_sesion=hacer_cerrar_sesion,
                        modulos_permitidos=modulos
                    ),
                    ft.Container(
                        expand=True,
                        padding=24,
                        bgcolor=COLOR_FONDO,
                        content=area_contenido
                    )
                ]
            )

        page.add(layout)
        page.update()

    def on_resize(e):
        if estado["usuario"]:
            reconstruir_layout()

    page.on_resize = on_resize
    mostrar_login()


ft.app(target=main)
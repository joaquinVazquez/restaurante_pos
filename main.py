# main.py
import sys, os, site
import logging

# 1. Configuración de entorno virtual (UNA SOLA VEZ)
venv_site_packages = site.getsitepackages()[0]
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Configuración inicial para evitar errores de referencia
logging.basicConfig(level=logging.INFO)

# 2. Importaciones de librerías
import flet as ft
from database.db_manager import verificar_conexion
from controllers.auth_controller import cerrar_sesion, get_modulos_permitidos



# 3. Importaciones de Vistas
from views.login_view import login_view
from views.sidebar import sidebar
from views.bottom_nav import bottom_nav
from views.ventas_view import ventas_view
from views.inicio_view import inicio_view
from views.productos_view import productos_view
from views.inventario_view import inventario_view
from views.reportes_view import reportes_view
from views.caja_view import caja_view
from views.clientes_view import clientes_view
from database.db_manager import verificar_conexion


COLOR_FONDO      = "#f0f4f8"
BREAKPOINT_MOVIL = 800
BOTTOM_NAV_H     = 72

try:
    verificar_conexion()
    logging.info("Conexión a Convex verificada correctamente")
except Exception:
    logging.critical("Falló verificar_conexion()", exc_info=True)
    raise

NAV_ITEMS = {
    "inicio":     ("🏠", "Inicio"),
    "ventas":     ("💰", "Ventas"),
    "productos":  ("📦", "Productos"),
    "inventario": ("📥", "Inventario"),
    "reportes":   ("📊", "Reportes"),
    "caja":       ("🏧", "Caja"),
    "clientes":   ("👥", "Clientes"),
    "config":     ("⚙️", "Config"),
}


def es_movil(page: ft.Page) -> bool:
    return page.width is not None \
        and page.width <= BREAKPOINT_MOVIL


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

    def hacer_nav_item(modulo, modulo_activo, on_cambiar):
        icono, label = NAV_ITEMS.get(modulo, ("●", modulo))
        activo = modulo == modulo_activo
        return ft.Container(
            expand=True,
            height=64,
            on_click=lambda e, m=modulo: on_cambiar(m),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    ft.Text(icono, size=20,
                            color="#00b894" if activo
                            else "#a0aec0"),
                    ft.Text(label, size=10,
                            color="white" if activo
                            else "#a0aec0",
                            weight=ft.FontWeight.BOLD if activo
                            else ft.FontWeight.NORMAL),
                ],
            ),
        )

    def mostrar_login():
        estado["usuario"] = None
        page.controls.clear()
        page.bgcolor = COLOR_FONDO
        page.add(login_view(page,
                            on_login_exitoso=mostrar_app))
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
        area_contenido.padding = 12 if es_movil(page) else 24

        # Loader
        area_contenido.content = ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(color="#00b894"),
                    ft.Text("Cargando...",
                            color="#7f8c8d", size=13)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        )
        page.update()

        try:
            if modulo == "inicio":
                contenido = inicio_view(
                    page, on_cambiar=cargar_modulo)
            elif modulo == "ventas":
                contenido = ventas_view(page)
            elif modulo == "productos":
                contenido = productos_view(page)
            elif modulo == "inventario":
                contenido = inventario_view(page)
            elif modulo == "reportes":
                contenido = reportes_view(page)
            elif modulo == "caja":
                contenido = caja_view(page)
            elif modulo == "clientes":
                contenido = clientes_view(page)
            elif modulo == "config":
                from views.config_view import config_view
                contenido = config_view(
                    page, usuario_actual=usuario)
            else:
                contenido = ft.Column(
                    controls=[
                        ft.Text(f"Módulo: {modulo}",
                                size=22,
                                weight=ft.FontWeight.BOLD),
                        ft.Text("Próximamente...", size=14),
                    ],
                )
        except Exception as ex:
            logging.error(f"Error al cargar módulo '{modulo}'", exc_info=True)
            contenido = ft.Text(f"ERROR: {ex}", color="red", size=14)

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
            layout = ft.Stack(
                width=page.width,
                height=page.height,
                controls=[
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(12, 12, 12, BOTTOM_NAV_H + 12),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=area_contenido,
                    ),
                    ft.Container(
                        left=0, right=0, bottom=0,
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


ft.run(main)



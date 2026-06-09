# views/login_view.py
import flet as ft
from controllers.auth_controller import login

COLOR_FONDO    = "#f0f4f8"
COLOR_TARJETA  = "#ffffff"
COLOR_ACENTO   = "#00b894"
COLOR_ROJO     = "#e74c3c"
COLOR_TEXTO    = "#2c3e50"
COLOR_SUBTEXTO = "#7f8c8d"


def login_view(page: ft.Page, on_login_exitoso):

    campo_usuario = ft.TextField(
        label="Usuario",
        hint_text="Ingresa tu usuario",
        border_radius=10,
        bgcolor="white",
        color=COLOR_TEXTO,
        width=320,
        on_submit=lambda e: intentar_login(e)
    )

    campo_password = ft.TextField(
        label="Contraseña",
        hint_text="Ingresa tu contraseña",
        password=True,
        can_reveal_password=True,
        border_radius=10,
        bgcolor="white",
        color=COLOR_TEXTO,
        width=320,
        on_submit=lambda e: intentar_login(e)
    )

    lbl_error = ft.Text(
        "",
        color=COLOR_ROJO,
        size=13,
        visible=False
    )

    btn_entrar = ft.ElevatedButton(
        "Entrar",
        bgcolor=COLOR_ACENTO,
        color="white",
        width=320,
        height=48,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=lambda e: intentar_login(e)
    )

    def intentar_login(e):
        lbl_error.visible   = False
        btn_entrar.disabled = True
        page.update()

        usuario = login(
            campo_usuario.value.strip(),
            campo_password.value.strip()
        )

        btn_entrar.disabled = False

        if usuario:
            on_login_exitoso(usuario)
        else:
            lbl_error.value   = "❌ Usuario o contraseña incorrectos"
            lbl_error.visible = True
            campo_password.value = ""
            page.update()

    return ft.Container(
        expand=True,
        bgcolor=COLOR_FONDO,
        content=ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("🍽️", size=64),
                            ft.Text(
                                "RestaurantePOS",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXTO
                            ),
                            ft.Text(
                                "Sistema de Punto de Venta",
                                size=13,
                                color=COLOR_SUBTEXTO
                            ),
                            ft.Container(height=24),
                            campo_usuario,
                            ft.Container(height=8),
                            campo_password,
                            ft.Container(height=4),
                            lbl_error,
                            ft.Container(height=12),
                            btn_entrar,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0
                    ),
                    bgcolor=COLOR_TARJETA,
                    border_radius=20,
                    padding=40,
                    shadow=ft.BoxShadow(
                        blur_radius=20,
                        color="#00000015",
                        offset=ft.Offset(0, 4)
                    )
                ),
                ft.Container(expand=True),
                ft.Text(
                    "v2.0 — RestaurantePOS",
                    size=11,
                    color=COLOR_SUBTEXTO
                ),
                ft.Container(height=16)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
    )
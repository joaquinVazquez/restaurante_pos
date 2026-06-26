import flet as ft
from database.db_manager import login_usuario, registrar_cuenta

COLOR_ACENTO = "#00b894"
COLOR_FONDO  = "#f0f4f8"
COLOR_TEXTO  = "#2c3e50"

def login_view(page: ft.Page, on_login_exitoso):
    modo_registro = False # False = Login, True = Registro

    lbl_titulo = ft.Text("Iniciar Sesión", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO)
    
    # Inputs compartidos
    txt_user = ft.TextField(label="Usuario", width=300, prefix_icon=ft.icons.PERSON)
    txt_pass = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True, prefix_icon=ft.icons.LOCK)
    
    # Inputs exclusivos de registro
    txt_negocio = ft.TextField(label="Nombre del Negocio", width=300, prefix_icon=ft.icons.STORE, visible=False)
    txt_nombre  = ft.TextField(label="Tu Nombre (Administrador)", width=300, prefix_icon=ft.icons.BADGE, visible=False)

    lbl_error = ft.Text("", color="red", size=12)

    def ejecutar_accion(e):
        lbl_error.value = ""
        page.update()
        
        if not txt_user.value or not txt_pass.value:
            lbl_error.value = "⚠️ Completa los campos obligatorios."
            page.update()
            return

        if modo_registro:
            if not txt_negocio.value or not txt_nombre.value:
                lbl_error.value = "⚠️ Completa todos los campos para registrarte."
                page.update()
                return
                
            ok, data = registrar_cuenta(
                txt_negocio.value, txt_nombre.value, 
                txt_user.value, txt_pass.value
            )
            if ok:
                on_login_exitoso(data)
            else:
                lbl_error.value = data
        else:
            user_data = login_usuario(txt_user.value, txt_pass.value)
            if user_data:
                on_login_exitoso(user_data)
            else:
                lbl_error.value = "❌ Credenciales incorrectas."
        page.update()

    def alternar_modo(e):
        nonlocal modo_registro
        modo_registro = not modo_registro
        
        if modo_registro:
            lbl_titulo.value = "Crear Cuenta"
            btn_accion.text = "Registrar y Entrar"
            btn_alternar.text = "¿Ya tienes cuenta? Inicia sesión"
            txt_negocio.visible = True
            txt_nombre.visible = True
        else:
            lbl_titulo.value = "Iniciar Sesión"
            btn_accion.text = "Entrar"
            btn_alternar.text = "¿Nuevo negocio? Crea una cuenta"
            txt_negocio.visible = False
            txt_nombre.visible = False
            
        lbl_error.value = ""
        page.update()

    btn_accion = ft.ElevatedButton("Entrar", bgcolor=COLOR_ACENTO, color="white", width=300, height=45, on_click=ejecutar_accion)
    btn_alternar = ft.TextButton("¿Nuevo negocio? Crea una cuenta", on_click=alternar_modo)

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.icons.POINT_OF_SALE, size=60, color=COLOR_ACENTO),
                lbl_titulo,
                ft.Divider(color="transparent", height=10),
                txt_negocio,
                txt_nombre,
                txt_user,
                txt_pass,
                lbl_error,
                btn_accion,
                btn_alternar
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        bgcolor="white",
        padding=40,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=15, color="#00000015", offset=ft.Offset(0, 5))
    )

    return ft.Container(
        content=formulario,
        alignment=ft.alignment.center,
        expand=True,
        bgcolor=COLOR_FONDO
    )
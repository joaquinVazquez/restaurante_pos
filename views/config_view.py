# views/config_view.py
import flet as ft
from database.db_manager import (
    get_configuracion, guardar_configuracion,
    get_usuarios, crear_usuario,
    cambiar_password_usuario, toggle_usuario_activo,
    get_categorias, crear_categoria,
    actualizar_categoria, eliminar_categoria,
    get_config_impresora, guardar_config_impresora,
)

COLOR_FONDO    = "#f0f4f8"
COLOR_TARJETA  = "#ffffff"
COLOR_TEXTO    = "#2c3e50"
COLOR_SUBTEXTO = "#7f8c8d"
COLOR_ACENTO   = "#00b894"
COLOR_ROJO     = "#e74c3c"


def config_view(page: ft.Page, usuario_actual: dict = None):

    def snack(texto, color=COLOR_ACENTO):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto, color="white"),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    def card(content):
        return ft.Container(
            content=content,
            bgcolor=COLOR_TARJETA,
            border_radius=12,
            padding=18,
            expand=True,
        )

    def cerrar_dialogo(dialog):
        dialog.open = False
        page.update()

    # ── Restaurante ────────────────────────────────────────
    config = get_configuracion() or {}

    import shutil, os
    RUTA_LOGO = "assets/logo"

    logo_actual = {"ruta": config.get("logo", "")}

    preview_logo = ft.Container(
        content=ft.Image(
            src=logo_actual["ruta"],
            width=80, height=80,
            fit=ft.ImageFit.CONTAIN
        ) if logo_actual["ruta"] and os.path.exists(logo_actual["ruta"])
        else ft.Text("🍽️", size=40),
        width=90, height=90,
        bgcolor=COLOR_FONDO,
        border_radius=12,
        alignment=ft.alignment.center,
        border=ft.border.all(1, "#e0e0e0")
    )

    def seleccionar_logo(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            archivo = e.files[0]
            os.makedirs(RUTA_LOGO, exist_ok=True)
            ruta_destino = os.path.join(
                RUTA_LOGO, f"logo_{archivo.name}")
            shutil.copy2(archivo.path, ruta_destino)
            logo_actual["ruta"] = ruta_destino
            preview_logo.content = ft.Image(
                src=ruta_destino,
                width=80, height=80,
                fit=ft.ImageFit.CONTAIN
            )
            guardar_configuracion({"logo": ruta_destino})
            snack("✅ Logo actualizado")
            page.update()

    file_picker_logo = ft.FilePicker(on_result=seleccionar_logo)
    page.overlay.append(file_picker_logo)
    nombre    = ft.TextField(label="Nombre del restaurante",
                              value=config.get(
                                  "nombre_restaurante", ""),
                              height=48)
    direccion = ft.TextField(label="Dirección",
                              value=config.get(
                                  "direccion", ""),
                              multiline=True)
    telefono  = ft.TextField(label="Teléfono",
                              value=config.get(
                                  "telefono", ""),
                              height=48)
    email     = ft.TextField(label="Email",
                              value=config.get(
                                  "email", ""),
                              height=48)
    rfc       = ft.TextField(label="RFC",
                              value=config.get(
                                  "rfc", ""),
                              height=48)

    def guardar_restaurante(e):
        guardar_configuracion({
            "nombre_restaurante": nombre.value,
            "direccion":          direccion.value,
            "telefono":           telefono.value,
            "email":              email.value,
            "rfc":                rfc.value,
        })
        # Recargar el valor en memoria para que persista en pantalla
        config["nombre_restaurante"] = nombre.value
        config["direccion"] = direccion.value
        config["telefono"] = telefono.value
        config["email"] = email.value
        config["rfc"] = rfc.value
        snack("✅ Datos del restaurante guardados")

    restaurante_tab = card(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Datos del Restaurante", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ft.Text("Aparecerán en los tickets PDF.",
                        size=13, color=COLOR_SUBTEXTO),
                        ft.Row(
                    controls=[
                        preview_logo,
                        ft.Column(
                            controls=[
                                ft.Text("Logo del restaurante",
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_TEXTO),
                                ft.Text("Aparecerá en tickets",
                                        size=11,
                                        color=COLOR_SUBTEXTO),
                                ft.ElevatedButton(
                                    "📁 Subir logo",
                                    bgcolor=COLOR_ACENTO,
                                    color="white",
                                    on_click=lambda e:
                                        file_picker_logo.pick_files(
                                            allowed_extensions=[
                                                "jpg", "jpeg",
                                                "png"]
                                        )
                                )
                            ],
                            spacing=4
                        )
                    ],
                    spacing=16
                ),
                ft.Divider(),
                nombre, direccion,
                ft.Row([telefono, email], spacing=12),
                rfc,
                ft.ElevatedButton(
                    "💾 Guardar cambios",
                    height=48,
                    bgcolor=COLOR_ACENTO,
                    color="white",
                    on_click=guardar_restaurante,
                ),
            ],
            spacing=12,
        )
    )

    # ── Usuarios ───────────────────────────────────────────
    usuarios_list  = ft.Column(spacing=8,
                                scroll=ft.ScrollMode.AUTO,
                                expand=True)
    nuevo_nombre   = ft.TextField(label="Nombre", height=48,
                                   expand=True)
    nuevo_username = ft.TextField(label="Usuario", height=48,
                                   expand=True)
    nuevo_password = ft.TextField(label="Contraseña",
                                   password=True,
                                   can_reveal_password=True,
                                   height=48, expand=True)
    nuevo_rol      = ft.Dropdown(
        label="Rol", value="cajero", height=48,
        options=[
            ft.dropdown.Option("cajero", "Cajero"),
            ft.dropdown.Option("admin",  "Admin"),
        ],
    )

    def cargar_usuarios():
        usuarios_list.controls.clear()
        for u in get_usuarios():
            es_actual = (usuario_actual and
                         u["id"] == usuario_actual.get("id"))
            activo = bool(u.get("activo", True))
            usuarios_list.controls.append(
                ft.Container(
                    bgcolor=COLOR_FONDO,
                    border_radius=10,
                    padding=12,
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                expand=True, spacing=2,
                                controls=[
                                    ft.Text(u["nombre"], size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_TEXTO),
                                    ft.Text(
                                        f"{u['username']} · {u['rol']}",
                                        size=12,
                                        color=COLOR_SUBTEXTO),
                                ],
                            ),
                            ft.Text(
                                "Activo" if activo else "Inactivo",
                                size=12,
                                color=COLOR_ACENTO if activo
                                else COLOR_ROJO
                            ),
                            ft.IconButton(
                                icon=ft.icons.LOCK_RESET,
                                tooltip="Cambiar contraseña",
                                on_click=lambda e, usr=u:
                                    abrir_dialogo_password(usr)
                            ),
                            ft.Switch(
                                value=activo,
                                disabled=es_actual,
                                on_change=lambda e, usr=u:
                                    cambiar_estado(usr,
                                                   e.control.value)
                            ),
                        ],
                    ),
                )
            )
        page.update()

    def agregar_usuario(e):
        if not nuevo_nombre.value or \
           not nuevo_username.value or \
           not nuevo_password.value:
            snack("⚠️ Completa todos los campos", COLOR_ROJO)
            return
        crear_usuario({
            "nombre":   nuevo_nombre.value,
            "username": nuevo_username.value,
            "password": nuevo_password.value,
            "rol":      nuevo_rol.value,
        })
        nuevo_nombre.value = nuevo_username.value = \
            nuevo_password.value = ""
        cargar_usuarios()
        snack("✅ Usuario creado")

    def cambiar_estado(usuario, activo):
        if usuario_actual and \
           usuario["id"] == usuario_actual.get("id"):
            snack("⚠️ No puedes desactivarte a ti mismo",
                  COLOR_ROJO)
            cargar_usuarios()
            return
        toggle_usuario_activo(usuario["id"], activo)
        cargar_usuarios()

    def abrir_dialogo_password(usuario):
        nueva_pwd = ft.TextField(
            label="Nueva contraseña",
            password=True,
            can_reveal_password=True,
            height=48,
        )

        def guardar_pwd(e):
            if not nueva_pwd.value:
                return
            cambiar_password_usuario(usuario["id"], nueva_pwd.value)
            dialog.open = False
            snack("✅ Contraseña actualizada")
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Cambiar contraseña: {usuario['username']}"),
            content=nueva_pwd,
            actions=[
                ft.TextButton("Cancelar",
                              on_click=lambda e:
                                  cerrar_dialogo(dialog)),
                ft.ElevatedButton("Guardar",
                                   bgcolor=COLOR_ACENTO,
                                   color="white",
                                   on_click=guardar_pwd),
            ],
        )
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    usuarios_tab = card(
        ft.Column(
            expand=True,
            controls=[
                ft.Text("Gestión de Usuarios", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ft.Row([nuevo_nombre, nuevo_username],
                       spacing=12),
                ft.Row([nuevo_password, nuevo_rol],
                       spacing=12),
                ft.ElevatedButton(
                    "➕ Agregar usuario",
                    height=48,
                    bgcolor=COLOR_ACENTO,
                    color="white",
                    on_click=agregar_usuario,
                ),
                ft.Divider(),
                usuarios_list,
            ],
            spacing=12,
        )
    )

    # ── Categorías ─────────────────────────────────────────
    categorias_list = ft.Column(spacing=8,
                                 scroll=ft.ScrollMode.AUTO,
                                 expand=True)
    cat_nombre = ft.TextField(label="Nombre", height=48,
                               expand=True)
    cat_icono  = ft.TextField(label="Ícono", hint_text="🍽️",
                               height=48, width=100)

    def cargar_cats():
        categorias_list.controls.clear()
        for c in get_categorias():
            categorias_list.controls.append(
                ft.Container(
                    bgcolor=COLOR_FONDO,
                    border_radius=10,
                    padding=12,
                    content=ft.Row(
                        controls=[
                            ft.Text(c.get("icono") or "🍽️",
                                    size=22),
                            ft.Text(c["nombre"], expand=True,
                                    size=14,
                                    weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                on_click=lambda e, cat=c:
                                    abrir_editar_cat(cat)
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=COLOR_ROJO,
                                on_click=lambda e, cat=c:
                                    eliminar_cat(cat)
                            ),
                        ],
                    ),
                )
            )
        page.update()

    def agregar_cat(e):
        if not cat_nombre.value:
            snack("⚠️ Escribe el nombre", COLOR_ROJO)
            return
        crear_categoria({
            "nombre": cat_nombre.value,
            "icono":  cat_icono.value or "🍽️",
        })
        cat_nombre.value = cat_icono.value = ""
        cargar_cats()
        snack("✅ Categoría creada")

    def abrir_editar_cat(categoria):
        n = ft.TextField(label="Nombre",
                         value=categoria["nombre"], height=48)
        i = ft.TextField(label="Ícono",
                         value=categoria.get("icono") or "",
                         height=48)

        def guardar(e):
            actualizar_categoria(categoria["id"],
                                  {"nombre": n.value,
                                   "icono": i.value})
            dialog.open = False
            cargar_cats()
            snack("✅ Categoría actualizada")
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar categoría"),
            content=ft.Column([n, i], tight=True, spacing=12),
            actions=[
                ft.TextButton("Cancelar",
                              on_click=lambda e:
                                  cerrar_dialogo(dialog)),
                ft.ElevatedButton("Guardar",
                                   bgcolor=COLOR_ACENTO,
                                   color="white",
                                   on_click=guardar),
            ],
        )
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def eliminar_cat(categoria):
        try:
            eliminar_categoria(categoria["id"])
            cargar_cats()
            snack("🗑️ Categoría eliminada")
        except Exception as ex:
            snack(str(ex), COLOR_ROJO)

    categorias_tab = card(
        ft.Column(
            expand=True,
            controls=[
                ft.Text("Categorías", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ft.Row([cat_nombre, cat_icono], spacing=12),
                ft.ElevatedButton(
                    "➕ Agregar categoría",
                    height=48,
                    bgcolor=COLOR_ACENTO,
                    color="white",
                    on_click=agregar_cat,
                ),
                ft.Divider(),
                categorias_list,
            ],
            spacing=12,
        )
    )

    # ── Impresora ──────────────────────────────────────────
    imp_config     = get_config_impresora() or {}
    imp_nombre     = ft.TextField(
        label="Nombre de impresora",
        value=imp_config.get("nombre_impresora", ""),
        height=48
    )
    ancho_papel    = ft.RadioGroup(
        value=str(imp_config.get("ancho_papel", "80")),
        content=ft.Row(controls=[
            ft.Radio(value="58", label="58mm"),
            ft.Radio(value="80", label="80mm"),
        ]),
    )
    mensaje_ticket = ft.TextField(
        label="Mensaje en tickets",
        value=imp_config.get("mensaje_ticket",
                              "¡Gracias por su compra!"),
        multiline=True,
        min_lines=2,
        max_lines=4,
    )

    def guardar_imp(e):
        guardar_config_impresora({
            "nombre_impresora": imp_nombre.value,
            "ancho_papel":      ancho_papel.value,
            "mensaje_ticket":   mensaje_ticket.value,
        })
        snack("✅ Configuración de impresora guardada")

    impresora_tab = card(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Impresora y Tickets", size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                imp_nombre,
                ft.Text("Ancho de papel:", size=13,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO),
                ancho_papel,
                mensaje_ticket,
                ft.ElevatedButton(
                    "🖨️ Guardar configuración",
                    height=48,
                    bgcolor=COLOR_ACENTO,
                    color="white",
                    on_click=guardar_imp,
                ),
            ],
            spacing=12,
        )
    )

    # ── Cargar datos iniciales ─────────────────────────────
    cargar_usuarios()
    cargar_cats()

    # ── Layout ─────────────────────────────────────────────
    return ft.Column(
        expand=True,
        spacing=12,
        controls=[
            ft.Text("⚙️ Configuración", size=22,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_TEXTO),
            ft.Tabs(
                selected_index=0,
                animation_duration=250,
                expand=True,
                tabs=[
                    ft.Tab(text="Restaurante",
                           content=restaurante_tab),
                    ft.Tab(text="Usuarios",
                           content=usuarios_tab),
                    ft.Tab(text="Categorías",
                           content=categorias_tab),
                    ft.Tab(text="Impresora",
                           content=impresora_tab),
                ],
            ),
        ],
    )
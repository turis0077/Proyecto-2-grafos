# interface/login.py

import solara
from database.db import Neo4jConnection  

def login_page():
    """
    Página de login/registro usando Solara. Permite:
      - Iniciar sesión verificando usuario y contraseña en Neo4j.
      - Crear un nuevo usuario (INSERT en Neo4j).
    """

    # Estado para alternar entre pestañas "login" y "register"
    mode = solara.use_state("login")

    # Campos para LOGIN
    username = solara.use_state("")
    password = solara.use_state("")
    login_message = solara.use_state("")

    # Campos para REGISTER
    new_username = solara.use_state("")
    new_password = solara.use_state("")
    confirm_password = solara.use_state("")
    register_message = solara.use_state("")

    # Instancia compartida de conexión a Neo4j
    conn = Neo4jConnection()

    def handle_login():
        login_message.set_value("")
        if not username.value or not password.value:
            login_message.set_value("Por favor, ingresa usuario y contraseña.")
            return
        # Verificar en Neo4j si existe el usuario y coincide la contraseña
        query = """
        MATCH (u:Usuario {nombre: $nombre})
        RETURN u.password AS pwd
        """
        resultados = conn.run_query(query, {"nombre": username.value})
        if not resultados:
            login_message.set_value("Usuario no encontrado.")
            return
        pwd_stored = resultados[0]["pwd"]
        if pwd_stored != password.value:
            login_message.set_value("Contraseña incorrecta.")
            return
        login_message.set_value(f"¡Bienvenido, {username.value}!")

    def handle_register():
        register_message.set_value("")
        if not new_username.value or not new_password.value or not confirm_password.value:
            register_message.set_value("Completa todos los campos.")
            return
        if new_password.value != confirm_password.value:
            register_message.set_value("Las contraseñas no coinciden.")
            return
        # Verificar que el usuario no exista
        query_check = """
        MATCH (u:Usuario {nombre: $nombre})
        RETURN u
        """
        existe = conn.run_query(query_check, {"nombre": new_username.value})
        if existe:
            register_message.set_value("Ese nombre de usuario ya está en uso.")
            return
        # Crear el nodo Usuario con propiedad password
        query_create = """
        CREATE (u:Usuario {nombre: $nombre, password: $password})
        """
        conn.run_query(query_create, {"nombre": new_username.value, "password": new_password.value})
        register_message.set_value("Usuario creado. Ahora puedes iniciar sesión.")
        # Limpiar campos
        new_username.set_value("")
        new_password.set_value("")
        confirm_password.set_value("")
        # Volver a pestaña de login
        mode.set_value("login")

    # --- Renderizado de UI con Solara ---
    with solara.Column(gap="1rem"):
        # Encabezado y botones de cambio de pestaña
        with solara.Row(gap="1rem"):
            solara.Button(
                "Iniciar Sesión",
                variant="primary" if mode.value == "login" else "outlined",
                on_click=lambda: mode.set_value("login"),
            )
            solara.Button(
                "Registrarse",
                variant="primary" if mode.value == "register" else "outlined",
                on_click=lambda: mode.set_value("register"),
            )

        if mode.value == "login":
            solara.Markdown("## Iniciar Sesión")
            solara.TextInput(
                label="Usuario",
                value=username.value,
                on_change=username.set_value,
                placeholder="Ingresa tu nombre de usuario",
            )
            solara.PasswordInput(
                label="Contraseña",
                value=password.value,
                on_change=password.set_value,
                placeholder="Ingresa tu contraseña",
            )
            solara.Button("Entrar", on_click=lambda: handle_login())
            if login_message.value:
                solara.Alert(login_message.value, status="info")

        else:  # mode == "register"
            solara.Markdown("## Crear Nuevo Usuario")
            solara.TextInput(
                label="Usuario",
                value=new_username.value,
                on_change=new_username.set_value,
                placeholder="Elige un nombre de usuario",
            )
            solara.PasswordInput(
                label="Contraseña",
                value=new_password.value,
                on_change=new_password.set_value,
                placeholder="Elige una contraseña",
            )
            solara.PasswordInput(
                label="Confirmar Contraseña",
                value=confirm_password.value,
                on_change=confirm_password.set_value,
                placeholder="Repite tu contraseña",
            )
            solara.Button("Registrar", on_click=lambda: handle_register())
            if register_message.value:
                solara.Alert(register_message.value, status="info")

    # Cerrar la conexión si la página se destruye
    solara.use_effect(lambda: conn.close(), [])


# Exportar el componente como página principal de login
login = login_page


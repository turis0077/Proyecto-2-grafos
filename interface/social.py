# interfaz/social.py

import solara
from datetime import date
from database.db import Neo4jConnection  

neo4j_conn = Neo4jConnection()

@solara.component
def Social():
    """
    Componente principal para la sección Social:
      - Muestra el dropdown de mascotas para filtrar comentarios.
      - Lista los comentarios de la mascota seleccionada.
      - Presenta un formulario para que el usuario envíe un nuevo comentario.
    """
    mascota_sel, set_mascota_sel = solara.use_state(None)
    lista_mascotas, set_lista_mascotas = solara.use_state([])
    comentarios, set_comentarios = solara.use_state([])
    texto, set_texto = solara.use_state("")

    # Cargar lista de todas las mascotas (una sola vez)
    solara.use_effect_once(lambda: cargar_mascotas())

    def cargar_mascotas():
        query = "MATCH (m:Mascota) RETURN id(m) AS id, m.raza AS raza"
        res = neo4j_conn.run_query(query)
        set_lista_mascotas([{"id": r["id"], "raza": r["raza"]} for r in res])

    def cargar_comentarios(id_mascota):
        if id_mascota is None:
            set_comentarios([])
            return
        query = """
        MATCH (u:Usuario)-[:COMENTA]->(c:Comentario)-[:SOBRE]->(m:Mascota)
        WHERE id(m) = $id_mascota
        RETURN u.nombre AS usuario, c.texto AS texto, c.fecha AS fecha
        ORDER BY c.fecha DESC
        """
        res = neo4j_conn.run_query(query, {"id_mascota": id_mascota})
        set_comentarios([{"usuario": r["usuario"], "texto": r["texto"], "fecha": r["fecha"]} for r in res])

    def on_change_mascota(value):
        set_mascota_sel(value)
        cargar_comentarios(value)

    def on_submit_comentario():
        user_id = usuario_global  # Asegúrate de definir usuario_global en algún lado
        if user_id is None or mascota_sel is None or not texto.strip():
            return
        # 1) Crear nodo Comentario y la relación con Usuario y Mascota
        query_insert = """
        CREATE (c:Comentario {texto: $texto, fecha: date($hoy)})
        WITH c
        MATCH (u:Usuario), (m:Mascota)
        WHERE id(u) = $user_id AND id(m) = $id_mascota
        CREATE (u)-[:COMENTA]->(c)-[:SOBRE]->(m)
        """
        neo4j_conn.run_query(
            query_insert,
            {
                "texto": texto,
                "hoy": date.today().isoformat(),
                "user_id": user_id,
                "id_mascota": mascota_sel
            },
        )
        # Limpiar textarea y recargar lista de comentarios
        set_texto("")
        cargar_comentarios(mascota_sel)

    return solara.Card([
            solara.Markdown("## Sección Social: Comentarios de Usuarios"),
            solara.Select(
                label="Elige una mascota",
                options=[(m["id"], m["raza"]) for m in lista_mascotas],
                value=mascota_sel,
                on_change=on_change_mascota,
            ),
            solara.Separator(),
            solara.Markdown("### Comentarios:"),
            *[
                solara.Card(
                    [
                        solara.Markdown(f"**{c['usuario']}** ({c['fecha']}):  \n{c['texto']}")
                    ],
                    style={"margin-bottom": "0.5rem"},
                )
                for c in comentarios
            ] or [solara.Markdown("_Sin comentarios aún_")],
            solara.Separator(),
            solara.TextArea("Escribe tu comentario", value=texto, on_change=set_texto),
            solara.Button("Enviar comentario", on_click=on_submit_comentario)
            ])

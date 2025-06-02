# interfaz/recomendaciones.py

import solara
from conexion.conexion_neo4j import Neo4jConnector
from recomendador.recomendador import Recomendador

neo4j_conn = Neo4jConnector()
reco = Recomendador(neo4j_conn)

@solara.component
def Recomendaciones():
    """
    Componente que muestra Top 5 mascotas sugeridas para el usuario en sesión.
    - Botón “Actualizar” para volver a consultar
    - Cada tarjeta muestra: imagen (si la tienes), raza, tipo, tamaño y botones opcionales.
    """
    recomendaciones, set_recomendaciones = solara.use_state([])
    cargando, set_cargando = solara.use_state(False)

    def load_recommendations():
        user_id = usuario_global
        if user_id is None:
            return
        set_cargando(True)
        top_ids = reco.recomendar_mascotas(user_id, top_n=5)
        detalles = []
        for mid in top_ids:
            query = """
            MATCH (m:Mascota)
            WHERE id(m) = $id_mascota
            RETURN m.raza AS raza, m.tipo AS tipo, m.tamaño AS tamaño
            """
            r = neo4j_conn.run_query(query, {"id_mascota": mid})
            if r:
                detalles.append({"id": mid, **r[0]})
        set_recomendaciones(detalles)
        set_cargando(False)

    return solara.Card(
        [
            solara.Button("Actualizar recomendaciones", on_click=load_recommendations),
            solara.Separator(),
            solara.If(
                cargando,
                solara.Markdown("Cargando recomendaciones…")
            ),
            *[
                solara.Card(
                    [
                        solara.Markdown(f"**Raza:** {d['raza']}  \n"
                                       f"**Tipo:** {d['tipo']}  \n"
                                       f"**Tamaño:** {d['tamaño']}")
                    ],
                    style={"margin-bottom": "1rem"}
                )
                for d in recomendaciones
            ]
        ]
    )
# scripts/inicializar_db.py

from db import Neo4jConnector

def crear_atributos(conn):
    """
    Crea todos los nodos Atributo que describen características compartidas
    por usuarios y mascotas (actividad, espacio, mantenimiento, alergias, etc.).
    """
    atributos = [
        "actividad baja", "actividad media", "actividad alta",
        "espacio pequeño", "espacio mediano", "espacio grande",
        "mantenimiento bajo", "mantenimiento medio", "mantenimiento alto",
        "alergias sí", "alergias no"
    ]
    for nombre in atributos:
        query = """
        MERGE (a:Atributo {nombre: $nombre})
        """
        conn.run_query(query, {"nombre": nombre})
    print("Atributos creados.")

def crear_mascotas(conn):
    """
    Crea nodos de ejemplo tipo Mascota y los relaciona con atributos.
    Ajusta estos datos conforme a las propiedades definidas en Neo4j.
    """
    mascotas = [
        {
            "raza": "Border Collie",
            "tipo": "perro",
            "tamaño": "mediano",
            "nivelEnergiaMedia": "alta",
            "personalidadMedia": "activa",
            "independiente": False,
            "curiosidad": True,
            "estimulacionMental": "alta",
            "alimentación": 3,
            "frecuenciaAseo": "medio",
            "propensoEnfermedades": ["displasia de cadera"],
            "atributos": ["actividad alta", "espacio mediano", "mantenimiento medio"]
        },
        {
            "raza": "Persa",
            "tipo": "gato",
            "tamaño": "pequeño",
            "nivelEnergiaMedia": "baja",
            "personalidadMedia": "tranquila",
            "independiente": True,
            "curiosidad": False,
            "estimulacionMental": "baja",
            "alimentación": 2,
            "frecuenciaAseo": "alto",
            "propensoEnfermedades": ["trastornos respiratorios"],
            "atributos": ["actividad baja", "espacio pequeño", "mantenimiento alto"]
        },
    ]

    for m in mascotas:
        # Crear o actualizar nodo Mascota con sus propiedades
        query_create = """
        MERGE (m:Mascota {raza: $raza})
          SET m.tipo = $tipo,
              m.tamaño = $tamaño,
              m.nivelEnergiaMedia = $nivelEnergiaMedia,
              m.personalidadMedia = $personalidadMedia,
              m.independiente = $independiente,
              m.curiosidad = $curiosidad,
              m.estimulacionMental = $estimulacionMental,
              m.alimentación = $alimentación,
              m.frecuenciaAseo = $frecuenciaAseo,
              m.propensoEnfermedades = $propensoEnfermedades
        """
        params_create = {
            "raza": m["raza"],
            "tipo": m["tipo"],
            "tamaño": m["tamaño"],
            "nivelEnergiaMedia": m["nivelEnergiaMedia"],
            "personalidadMedia": m["personalidadMedia"],
            "independiente": m["independiente"],
            "curiosidad": m["curiosidad"],
            "estimulacionMental": m["estimulacionMental"],
            "alimentación": m["alimentación"],
            "frecuenciaAseo": m["frecuenciaAseo"],
            "propensoEnfermedades": m["propensoEnfermedades"],
        }
        conn.run_query(query_create, params_create)

        # Relacionar cada mascota con sus atributos
        for nombre_atributo in m["atributos"]:
            query_rel = """
            MATCH (m:Mascota {raza: $raza}), (a:Atributo {nombre: $atributo})
            MERGE (m)-[:POSEE]->(a)
            """
            conn.run_query(query_rel, {"raza": m["raza"], "atributo": nombre_atributo})

    print("Mascotas creadas y relacionadas con atributos.")

def crear_usuarios(conn):
    """
    Crea algunos usuarios de prueba y los relaciona con atributos
    y recomendaciones previas. Útil para simular datos de colaboración.
    """
    usuarios = [
        {
            "nombre": "UsuarioEjemplo1",
            "actividad": "alta",
            "espacioVivienda": "mediano",
            "tiempoLibreCuidado": 2,
            "alergias": False,
            "atributos": ["actividad alta", "espacio mediano", "alergias no"]
        },
        {
            "nombre": "UsuarioEjemplo2",
            "actividad": "baja",
            "espacioVivienda": "pequeño",
            "tiempoLibreCuidado": 1,
            "alergias": True,
            "atributos": ["actividad baja", "espacio pequeño", "alergias sí"]
        },
    ]

    for u in usuarios:
        # Crear o actualizar nodo Usuario con sus propiedades
        query_create = """
        MERGE (u:Usuario {nombre: $nombre})
          SET u.actividad = $actividad,
              u.espacioVivienda = $espacioVivienda,
              u.tiempoLibreCuidado = $tiempoLibreCuidado,
              u.alergias = $alergias
        """
        params_create = {
            "nombre": u["nombre"],
            "actividad": u["actividad"],
            "espacioVivienda": u["espacioVivienda"],
            "tiempoLibreCuidado": u["tiempoLibreCuidado"],
            "alergias": u["alergias"],
        }
        conn.run_query(query_create, params_create)

        # Eliminar relaciones TIENE_ESTILO anteriores (en caso de actualización)
        query_del = """
        MATCH (u:Usuario {nombre: $nombre})-[r:TIENE_ESTILO]->(:Atributo)
        DELETE r
        """
        conn.run_query(query_del, {"nombre": u["nombre"]})

        # Crear relaciones TIENE_ESTILO con sus atributos
        for nombre_atributo in u["atributos"]:
            query_rel = """
            MATCH (u:Usuario {nombre: $nombre}), (a:Atributo {nombre: $atributo})
            MERGE (u)-[:TIENE_ESTILO]->(a)
            """
            conn.run_query(query_rel, {"nombre": u["nombre"], "atributo": nombre_atributo})

    # Crear una recomendación de prueba: UsuarioEjemplo1 recomendó Border Collie
    query_rec = """
    MATCH (u:Usuario {nombre: 'UsuarioEjemplo1'}), (m:Mascota {raza: 'Border Collie'})
    MERGE (u)-[r:RECOMIENDA]->(m)
      SET r.fecha = date('2025-05-01'), r.puntuación = 4
    """
    conn.run_query(query_rec)

    print("Usuarios de prueba creados, relacionados y recomendaciones simuladas.")

def main():
    con = Neo4jConnector()

    crear_atributos(con)
    crear_mascotas(con)
    crear_usuarios(con)

    con.close()
    print("Base de datos inicializada y conexión cerrada.")

if __name__ == "__main__":
    main()

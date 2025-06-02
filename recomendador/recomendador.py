import heapq
from db import Neo4jConnection

class Recomendador:
    def __init__(self, neo4j_conn: Neo4jConnection):
        self.db = neo4j_conn
    
    def obtener_atributos_usuario(self, id_usuario: int) -> list[str]:
        # (type hints) id_usuario es int, retoma una lista de strings
        """
        Consulta Neo4j para obtener la lista de nombres de atributos asociados al usuario y sus  parametros.
        Retorna una lista de nombres de atributos (ej. ["actividad alta", "espacio mediano", ...]).
        """

        query = """
        MATCH (u:Usuario)-[:TIENE_ESTILO]->(a:Atributo)
        WHERE id(u) = $id_usuario
        RETURN a.nombre AS atributo
        """
        resultados = self.db.run_query(query, {"id_usuario": id_usuario})
        return [r["atributo"] for r in resultados]
    
    def construir_grafo_local(self, atributos_usuario: list[str]) -> dict[str, dict[str, int]]:
        # (type hints) atributos_usuario es una lista de strings, retorna un diccionario
        """
        Arma un grafo en la memoria con los atributos del usuario conectandolo con los nodos de Mascota que tienen ese atributo con peso = 1.
        Cada nodo se representa como M_{id_mascota} donde id_mascota es el identificador de la mascota.
        Cada nodo de mascota inicializa sin conexiones.

        Equivalente Cypher para obtener mascotas de un atributo dado:
            MATCH (m:Mascota)-[:POSEE]->(a:Atributo {nombre: $atributo})
            RETURN id(m) AS id_mascota
        """
        
        grafo: dict[str, dict[str, int]] = {}
        grafo["Usuario"] = {}

        for a in atributos_usuario:
            grafo["Usuario"][a] = 1

        for a in atributos_usuario:
            query = """
            MATCH (m:Mascota)-[:POSEE]->(a:Atributo {nombre: $atributo})
            RETURN id(m) AS id_mascota
            """
            resultados = self.db.run_query(query, {"atributo": a})

            grafo.setdefault(a, {})

            for fila in resultados:
                id_m = fila["id_mascota"]
                etiqueta = f"M_{id_m}"
                # Conecta atributo mascota con peso 1
                grafo[a][etiqueta] = 1
                # Asegura la existencia de la entrada de la mascota en el grafo
                grafo.setdefault(etiqueta, {})

        return grafo
    
    def dijkstra(
        self,
        grafo: dict[str, dict[str, int]],
        origen: str) -> tuple[dict[str, float], dict[str, str | None]]:
        # (type hints) grafo es un diccionario. origen es un string que retorna una tupla de dos diccionarios (uno del tipo float y otro de str o None)
        """
        Implementación del algoritmo Dijkstra sobre el grafo construido en memoria.
        Recibe un grafo representado como un diccionario de adyacencia y un nodo de origen (como usuario).
        Devuelve dos diccionarios:
        - distancias: contiene la distancia mínima desde el nodo origen a cada nodo del grafo.
        - padres: contiene el nodo padre de cada nodo en el camino más corto desde el origen.
        """
        distancias = {nodo: float("inf") for nodo in grafo}
        padres: dict[str, str | None] = {nodo: None for nodo in grafo}
        distancias[origen] = 0

        heap: list[tuple[float, str]] = [(0, origen)]

        while heap:
            d_actual, nodo = heapq.heappop(heap)
            if d_actual > distancias[nodo]:
                continue
            for vecino, peso in grafo[nodo].items():
                nueva_dist = d_actual + peso
                if nueva_dist < distancias[vecino]:
                    distancias[vecino] = nueva_dist
                    padres[vecino] = nodo
                    heapq.heappush(heap, (nueva_dist, vecino))

        return distancias, padres
        
    
    def recomendar_mascotas(self, id_usuario: int, top_n: int = 5) -> list[str]:
        # (type hints) id_usuario es int, top_n es int, retorna una lista de strings
        """
        Genera una lista de los ID de las top_n mascotas recomendadas para cada usuario.
        Utiliza el algoritmo de Dijkstra para encontrar las distancias mínimas desde el nodo Usuario a los nodos Mascota.
        Primero obtiene los atributos del usuario, construye un grafo en memoria que conecta "Usuario" con esos atributos y 
        luego cada atributo con las mascotas que los poseen.
        """
        atributos = self.obtener_atributos_usuario(id_usuario)

        grafo = self.construir_grafo_local(atributos)

        distancias, _ = self.dijkstra(grafo, "Usuario")

        recomendaciones: list[tuple[float, int]] = []

        for nodo, distancia in distancias.items():
            if not nodo.startswith("M_"):
                continue
            id_mascota = int(nodo.split("_", 1)[1])

            query_score = """
            MATCH (:Usuario)-[r:RECOMIENDA]->(m:Mascota)
            WHERE id(m) = $id_mascota
            RETURN avg(r.puntuación) AS score
            """
            resultado_score = self.db.run_query(query_score, {"id_mascota": id_mascota})
            score = resultado_score[0]["score"] or 0

            puntaje_final = (1 / (1 + distancia)) * 0.7 + score * 0.3
            recomendaciones.append((puntaje_final, id_mascota))

        recomendaciones.sort(key=lambda x: x[0], reverse=True)
        top_ids = [id_m for (_, id_m) in recomendaciones[:top_n]]
        return top_ids

"""Ejecucion manual del archivo para pruebas"""   
if __name__ == "__main__":
    conn = Neo4jConnector()
    reco = Recomendador(conn)
    top_mas = reco.recomendar_mascotas(id_usuario=0, top_n=5)
    print("Top recomendaciones:", top_mas)
    conn.close()
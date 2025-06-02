import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Neo4jConnection:
    """
    Encapsula la conexion a Neo4j Aura y expone un metodo genérico run_query(...)
    que abre una sesion, ejecuta una consulta y devuelve los resultados.
    """
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        if not uri or not user or not pwd:
            raise RuntimeError("Faltan variables de entorno para la conexión a Neo4j")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))


    def close(self):
        self.driver.close()

    """
    Ejecuta una consulta en la base de datos Neo4j y devuelve los resultados.
    :param query: Consulta Cypher a ejecutar.
    :param parameters: Parámetros opcionales para la consulta.
    :return: Resultados de la consulta.
    """
    def run_query(self, query, parameters: dict = None):
 
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)

"""
Función de prueba manual.
Solo se ejecuta si corres 'python db.py' directamente.
Se encarga de verificar que la conexion este bien configurada en .env.
"""
def test_conexion():
    try:
        conn = Neo4jConnection()
    except RuntimeError as e:
        print(f"Error al leer .env: {e}")
        return

    with conn.driver.session() as session:
        result = session.run("RETURN 'Conexión exitosa' AS mensaje")
        for record in result:
            print(record["mensaje"])
    conn.close()

if __name__ == "__main__":
    test_conexion()

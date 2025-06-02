import pytest
from database.db import Neo4jConnection

@pytest.fixture(scope="module")
def neo4j_conn():
    """
    Crea una instancia de Neo4jConnection antes de las pruebas y la cierra después.
    """
    conn = Neo4jConnection()
    yield conn
    conn.close()

def test_conexion_simple(neo4j_conn):
    """
    Verifica que una consulta trivial retorne el valor esperado.
    """
    resultado = neo4j_conn.run_query("RETURN 1 AS uno")
    assert resultado, "No se obtuvieron resultados de la consulta"
    assert resultado[0]["uno"] == 1

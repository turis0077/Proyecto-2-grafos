import pytest
from recomendador.recomendador import Recomendador
from database.db import Neo4jConnection

def test_dijkstra_basico():
    """
    Prueba la implementación de Dijkstra con un grafo dummy en memoria:
      Usuario --1--> A
      A       --1--> M_1
      A       --2--> M_2
    Distancias esperadas:
      Usuario: 0
      A:       1
      M_1:     2
      M_2:     3
    """
    dummy_grafo = {
        "Usuario": {"A": 1},
        "A": {"M_1": 1, "M_2": 2},
        "M_1": {},
        "M_2": {}
    }
    rec = Recomendador(None)  # No necesita conexión para dijkstra
    distancias, padres = rec.dijkstra(dummy_grafo, "Usuario")
    assert distancias["Usuario"] == 0
    assert distancias["A"] == 1
    assert distancias["M_1"] == 2
    assert distancias["M_2"] == 3

@pytest.fixture(scope="module")
def neo4j_conn():
    """
    Crea y cierra Neo4jConnection para las pruebas de recomendación.
    """
    conn = Neo4jConnection()
    yield conn
    conn.close()

def test_recomendar_mascotas_sin_error(monkeypatch, neo4j_conn):
    """
    Verifica que recomendar_mascotas() no arroje excepciones cuando no hay datos en la base.
    Patch de construir_grafo_local para simular un grafo vacío (solo "Usuario").
    """
    rec = Recomendador(neo4j_conn)

    # Simular atributos del usuario (aunque no se usen porque construiremos un grafo vacío).
    monkeypatch.setattr(rec, "obtener_atributos_usuario", lambda id_usuario: ["actividad alta"])

    # Hacer que construir_grafo_local devuelva únicamente el nodo "Usuario" sin aristas.
    monkeypatch.setattr(rec, "construir_grafo_local", lambda attrs: {"Usuario": {}})

    # Si no hay nodos "M_<id>", no se invocará la consulta de puntuaciones y top será lista vacía.
    top = rec.recomendar_mascotas(id_usuario=0, top_n=3)
    assert isinstance(top, list)
    assert top == []

from neo4j import GraphDatabase

# Conexion a la base de datos Neo4j
uri = "neo4j+s://7dd9a6b8.databases.neo4j.io"
user = "neo4j"
password = "9iJnY5FwUr8_pfSlcu1EOjg8ofxzuE6hKFfd6NnBQr8"

driver = GraphDatabase.driver(uri, auth=(user, password))

# Probar la conexion
def test_conexion():
    with driver.session() as session:
        result = session.run("RETURN 'Conexión exitosa' AS mensaje")
        for record in result:
            print(record["mensaje"])

test_conexion()

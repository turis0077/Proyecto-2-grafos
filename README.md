# Proyecto2: Sistema de recomendaciones por grafos
Mascotas Según el Estilo de Vida del Usuario <br  />
**Grupo 10** <br  />
- Axel Cruz, 24656 <br  />
- Enya Gálvez, 24693<br  /><br  /><br  />

**Prerrequisitos**
- Python 3.8 o superior
- Cuenta con instancia activa de Neo4j Aura<br  /><br  /><br  />

**Instalación**
1. Inicializar entorno virtual de python desde cmd: <br  />
python -m venv env <br  />
env\Scripts\activate <br  />
2. Instalar dependencias (desde cmd): <br  />
pip install -r requirements.txt <br  />
3. Cambiar credenciales de Neo4j Aura a las de su instancia de Neo4j Aura en el archivo  ***.env*** <br  /><br  /><br  />
**Inicializar base de datos**
- Ejecutar: python -m recomendador.inicializar_db
<br  />

**Ejecutar aplicación**
- solara run interface/app.py
<br  />

**Pruebas unitarias**
- pytest tests/test_db.py
- pytest tests/test_recomendador.py







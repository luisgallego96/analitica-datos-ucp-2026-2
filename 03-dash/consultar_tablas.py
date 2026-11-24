from database import engine
from sqlalchemy import text

with engine.connect() as conexion:
    consulta = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)

    resultado = conexion.execute(consulta)

    print("Tablas encontradas:")

    for fila in resultado:
        print(fila[0])
from database import engine
from sqlalchemy import text

with engine.connect() as conexion:
    consulta = text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'logs'
        ORDER BY ordinal_position
    """)

    resultado = conexion.execute(consulta)

    print("ESTRUCTURA DE LA TABLA LOGS")
    print("----------------------------")

    for fila in resultado:
        print(f"Columna: {fila[0]} | Tipo: {fila[1]}")
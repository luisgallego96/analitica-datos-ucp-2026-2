from database import engine
from sqlalchemy import text

with engine.connect() as conexion:
    consulta = text("""
        SELECT status_code, COUNT(*) AS total
        FROM logs
        GROUP BY status_code
        ORDER BY status_code
    """)

    resultado = conexion.execute(consulta)

    print("CODIGOS DE RESPUESTA HTTP")
    print("-------------------------")

    for fila in resultado:
        print(f"HTTP {fila[0]}: {fila[1]} registros")
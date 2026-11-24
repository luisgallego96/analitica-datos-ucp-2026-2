from database import engine
from sqlalchemy import text

with engine.connect() as conexion:
    consulta = text("""
        SELECT svc, COUNT(*) AS total
        FROM logs
        GROUP BY svc
        ORDER BY total DESC
    """)

    resultado = conexion.execute(consulta)

    print("SERVICIOS REGISTRADOS")
    print("---------------------")

    for fila in resultado:
        print(f"Servicio: {fila[0]} | Registros: {fila[1]}")
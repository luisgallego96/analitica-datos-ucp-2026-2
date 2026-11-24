from database import engine
from sqlalchemy import text

with engine.connect() as conexion:
    consulta = text("""
        SELECT
            COUNT(*) AS total,
            MIN(ts) AS fecha_inicial,
            MAX(ts) AS fecha_final,
            COUNT(*) FILTER (WHERE svc IS NULL) AS servicios_nulos,
            COUNT(*) FILTER (WHERE status_code IS NULL) AS estados_nulos,
            COUNT(*) FILTER (WHERE duration IS NULL) AS duraciones_nulas
        FROM logs
    """)

    fila = conexion.execute(consulta).fetchone()

    print("RESUMEN GENERAL DE LOGS")
    print("-----------------------")
    print("Total de registros:", fila[0])
    print("Fecha inicial:", fila[1])
    print("Fecha final:", fila[2])
    print("Servicios nulos:", fila[3])
    print("Estados HTTP nulos:", fila[4])
    print("Duraciones nulas:", fila[5])
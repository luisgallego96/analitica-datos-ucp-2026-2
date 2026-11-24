from database import engine
from sqlalchemy import text

with engine.connect() as conexion:
    consulta = text("""
        SELECT
            COUNT(*) AS total,
            MIN(duration) AS minimo,
            MAX(duration) AS maximo,
            ROUND(AVG(duration), 2) AS promedio,
            PERCENTILE_CONT(0.95)
                WITHIN GROUP (ORDER BY duration) AS p95,
            PERCENTILE_CONT(0.99)
                WITHIN GROUP (ORDER BY duration) AS p99
        FROM logs
    """)

    resultado = conexion.execute(consulta).fetchone()

    print("ANALISIS DE DURACION")
    print("--------------------")
    print("Total:", resultado[0])
    print("Mínimo:", resultado[1])
    print("Máximo:", resultado[2])
    print("Promedio:", resultado[3])
    print("P95:", resultado[4])
    print("P99:", resultado[5])
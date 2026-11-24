

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Leer las variables del archivo .env
load_dotenv()

# Obtener la URI de PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear la conexión
if not DATABASE_URL:
    raise ValueError("No se encontró DATABASE_URL en .env")

engine = create_engine(DATABASE_URL)

# Comprobar la conexión
def probar_conexion():
    with engine.connect() as conexion:
        resultado = conexion.execute(text("SELECT 1"))
        return resultado.scalar()

if __name__ == "__main__":
    print("Probando conexión con PostgreSQL...")

    try:
        print("Resultado:", probar_conexion())
        print("¡Conexión exitosa!")
    except Exception as error:
        print("Error de conexión:", error)


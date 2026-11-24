# Monitor de Servicios - Analitica de Datos

## 1. Descripcion del proyecto

Este proyecto consiste en un dashboard desarrollado con Python y Dash para monitorear el comportamiento de diferentes servicios a partir de registros (logs) almacenados en una base de datos PostgreSQL.

El objetivo es visualizar indicadores de rendimiento, tiempos de respuesta y errores HTTP, facilitando el seguimiento del estado de los servicios.

## 2. Tecnologias utilizadas

- Python
- Dash
- Plotly
- Pandas
- PostgreSQL
- SQLAlchemy
- Psycopg
- Python-dotenv
- uv

## 3. Funcionalidades del dashboard

El dashboard permite:

- Seleccionar el servicio que se desea monitorear.
- Filtrar la informacion por periodos de 1, 3 y 24 horas.
- Consultar el tiempo promedio de respuesta (Response Time).
- Consultar el rendimiento de solicitudes por minuto (Throughput RPM).
- Visualizar la cantidad de errores HTTP 4xx y 5xx (Error Count).
- Consultar los percentiles P95 y P99 del tiempo de respuesta.
- Visualizar graficas de tiempos de respuesta y codigos de estado HTTP.
- Actualizar automaticamente la informacion cada 10 o 60 segundos.

## 4. Estructura del proyecto

- app.py: contiene el codigo principal del dashboard.
- app_original.py: conserva el dashboard original de ventas utilizado como referencia.
- database.py: establece y prueba la conexion con PostgreSQL.
- consultar_columnas.py: consulta las columnas de la base de datos.
- consultar_duracion.py: consulta estadisticas de duracion.
- consultar_estados.py: consulta los codigos de estado HTTP.
- consultar_resumen.py: consulta un resumen general de los registros.
- consultar_servicios.py: consulta los servicios disponibles.
- consultar_tablas.py: consulta las tablas de la base de datos.
- pyproject.toml: contiene la configuracion y dependencias del proyecto.
- uv.lock: registra las versiones de las dependencias.

## 5. Instalacion y ejecucion

1. Abrir PowerShell.
2. Ubicarse en la carpeta del proyecto:

   cd 03-dash

3. Instalar las dependencias:

   uv sync

4. Configurar la variable de entorno DATABASE_URL en un archivo .env con la URI de conexion proporcionada para PostgreSQL.

5. Ejecutar el dashboard:

   uv run python app.py

6. Abrir en el navegador:

   http://127.0.0.1:8050/

Para detener la aplicacion, regresar a PowerShell y presionar Ctrl + C.

## 6. Conexion a la base de datos

La aplicacion utiliza PostgreSQL como fuente de datos. La conexion se configura mediante la variable DATABASE_URL almacenada en el archivo .env.

Por seguridad, el archivo .env no debe subirse al repositorio, ya que contiene informacion privada de conexion.

## 7. Resultado esperado

Al ejecutar la aplicacion, se visualiza un dashboard interactivo que permite monitorear los servicios, analizar sus tiempos de respuesta, identificar errores HTTP y consultar indicadores de rendimiento mediante filtros y actualizaciones automaticas.

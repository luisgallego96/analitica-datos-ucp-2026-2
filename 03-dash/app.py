
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, callback
from sqlalchemy import text

from database import engine


app = Dash(__name__)
app.title = "Monitor de Servicios"


ESTILOS = {
    "background": "#F4F6FA",
    "card": "#FFFFFF",
    "text": "#202938",
    "blue": "#2563EB",
    "red": "#DC2626",
    "green": "#16A34A",
}


def obtener_datos(servicio, periodo):
    ahora = datetime.now(timezone.utc)

    horas = {
        "1": 1,
        "3": 3,
        "24": 24,
    }

    fecha_inicio = ahora - timedelta(hours=horas[periodo])

    consulta = text("""
        SELECT
            ts,
            svc,
            status_code,
            duration
        FROM logs
        WHERE ts >= :fecha_inicio
          AND ts <= :fecha_final
          AND (:servicio = 'Todos' OR svc = :servicio)
        ORDER BY ts
    """)

    with engine.connect() as conexion:
        df = pd.read_sql(
            consulta,
            conexion,
            params={
                "fecha_inicio": fecha_inicio,
                "fecha_final": ahora,
                "servicio": servicio,
            },
        )

    return df


def crear_tarjeta(titulo, valor, unidad="", color=None):
    return html.Div(
        [
            html.P(titulo, style={
                "color": "#64748B",
                "fontSize": "14px",
                "marginBottom": "8px",
            }),
            html.H2(
                f"{valor} {unidad}",
                style={
                    "color": color or ESTILOS["text"],
                    "fontSize": "27px",
                    "margin": "0",
                },
            ),
        ],
        style={
            "backgroundColor": "white",
            "padding": "22px",
            "borderRadius": "12px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
        },
    )


app.layout = html.Div(
    [
        html.H1(
            "Monitor de Servicios",
            style={"color": "#1E293B"},
        ),

        html.P(
            "Monitoreo de rendimiento y errores de PostgreSQL",
            style={"color": "#64748B"},
        ),

        html.Div(
            [
                html.Div([
                    html.Label("Seleccionar servicio"),
                    dcc.Dropdown(
                        id="servicio",
                        options=[
                            {"label": "Todos los servicios", "value": "Todos"},
                            {"label": "Catalog", "value": "catalog"},
                            {"label": "Checkout", "value": "checkout"},
                            {"label": "Users", "value": "users"},
                            {"label": "Auth", "value": "auth"},
                            {"label": "Payments", "value": "payments"},
                        ],
                        value="Todos",
                        clearable=False,
                    ),
                ], style={"width": "48%"}),

                html.Div([
                    html.Label("Período de consulta"),
                    dcc.Dropdown(
                        id="periodo",
                        options=[
                            {"label": "Última hora", "value": "1"},
                            {"label": "Últimas 3 horas", "value": "3"},
                            {"label": "Últimas 24 horas", "value": "24"},
                        ],
                        value="1",
                        clearable=False,
                    ),
                ], style={"width": "48%"}),
            ],
            style={
                "display": "flex",
                "gap": "20px",
                "marginBottom": "25px",
            },
        ),

        html.Div(
            id="indicadores",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(5, 1fr)",
                "gap": "15px",
                "marginBottom": "25px",
            },
        ),

        html.Div(
            [
                html.Div([
                    html.H3("Tiempo de respuesta"),
                    dcc.Graph(id="grafico-tiempo"),
                ], style={
                    "backgroundColor": "white",
                    "padding": "15px",
                    "borderRadius": "12px",
                }),

                html.Div([
                    html.H3("Códigos HTTP"),
                    dcc.Graph(id="grafico-errores"),
                ], style={
                    "backgroundColor": "white",
                    "padding": "15px",
                    "borderRadius": "12px",
                }),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "20px",
            },
        ),

        html.Div(
            [
                html.Label("Frecuencia de actualización"),
                dcc.Dropdown(
                    id="frecuencia",
                    options=[
                        {"label": "Cada 10 segundos", "value": 10000},
                        {"label": "Cada 60 segundos", "value": 60000},
                    ],
                    value=10000,
                    clearable=False,
                    style={"maxWidth": "300px"},
                ),
            ],
            style={"marginTop": "25px"},
        ),

        dcc.Interval(
            id="actualizacion",
            interval=10000,
            n_intervals=0,
        ),

        html.Div(id="ultima-actualizacion"),

    ],
    style={
        "backgroundColor": ESTILOS["background"],
        "minHeight": "100vh",
        "padding": "30px",
        "fontFamily": "Arial",
    },
)


@callback(
    Output("actualizacion", "interval"),
    Input("frecuencia", "value"),
)
def cambiar_frecuencia(frecuencia):
    return frecuencia


@callback(
    Output("indicadores", "children"),
    Output("grafico-tiempo", "figure"),
    Output("grafico-errores", "figure"),
    Output("ultima-actualizacion", "children"),
    Input("servicio", "value"),
    Input("periodo", "value"),
    Input("actualizacion", "n_intervals"),
)
def actualizar_dashboard(servicio, periodo, n_intervals):

    try:
        df = obtener_datos(servicio, periodo)

        if df.empty:
            vacio = go.Figure()
            vacio.update_layout(
                title="No hay registros en el período seleccionado"
            )

            return (
                [crear_tarjeta("Registros", "0")],
                vacio,
                vacio,
                "Sin datos para mostrar",
            )

        total = len(df)

        promedio = round(df["duration"].mean(), 2)
        p95 = round(df["duration"].quantile(0.95), 2)
        p99 = round(df["duration"].quantile(0.99), 2)

        errores_4xx = int(
            df["status_code"].between(400, 499).sum()
        )

        errores_5xx = int(
            df["status_code"].between(500, 599).sum()
        )

        errores = errores_4xx + errores_5xx

        minutos_periodo = int(periodo) * 60

        rpm = round(total / minutos_periodo, 2)

        indicadores = [
            crear_tarjeta("Response Time", promedio, "ms"),
            crear_tarjeta("Throughput", rpm, "RPM"),
            crear_tarjeta("Error Count", errores, "", "#DC2626"),
            crear_tarjeta("P95", p95, "ms"),
            crear_tarjeta("P99", p99, "ms"),
        ]

        grafico_tiempo = px.line(
            df,
            x="ts",
            y="duration",
            title="Evolución del tiempo de respuesta",
            labels={
                "ts": "Fecha y hora",
                "duration": "Duración (ms)",
            },
        )

        grafico_tiempo.update_layout(
            template="plotly_white",
            hovermode="x unified",
        )

        estados = (
            df.groupby("status_code")
            .size()
            .reset_index(name="cantidad")
        )

        # Clasificar los códigos HTTP por categoría
        estados["categoria"] = estados["status_code"].apply(
            lambda codigo:
                "Éxito (2xx)" if 200 <= codigo <= 299
                else "Error del cliente (4xx)" if 400 <= codigo <= 499
                else "Error del servidor (5xx)" if 500 <= codigo <= 599
                else "Otros"
        )

        grafico_errores = px.bar(
            estados,
            x="status_code",
            y="cantidad",
            color="categoria",
            title="Distribución de solicitudes por código HTTP",
            labels={
                "status_code": "Código HTTP",
                "cantidad": "Número de solicitudes",
                "categoria": "Categoría",
            },
            color_discrete_map={
                "Éxito (2xx)": "#16A34A",
                "Error del cliente (4xx)": "#F59E0B",
                "Error del servidor (5xx)": "#DC2626",
                "Otros": "#64748B",
            },
        )

        grafico_errores.update_layout(
            template="plotly_white",
            showlegend=True,
            xaxis_title="Código HTTP",
            yaxis_title="Número de solicitudes",
        )

        hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        return (
            indicadores,
            grafico_tiempo,
            grafico_errores,
            f"Última actualización: {hora}",
        )

    except Exception as error:
        vacio = go.Figure()
        vacio.update_layout(title="Error al consultar los datos")

        return (
            [crear_tarjeta("Estado", "Error", color="#DC2626")],
            vacio,
            vacio,
            f"No se pudo actualizar el dashboard: {error}",
        )


if __name__ == "__main__":
    app.run(debug=True)

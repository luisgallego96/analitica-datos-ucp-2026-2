from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go


app = Dash()
rng = np.random.default_rng(42)
catalogo = pd.DataFrame([
    ("Portátil", "Equipos", 2400000, 1980000),
    ("Teléfono", "Equipos", 1500000, 1125000),
    ("Tableta", "Equipos", 1100000, 770000),
    ("Monitor", "Equipos", 850000, 552500),
    ("Teclado", "Accesorios", 130000, 65000),
    ("Mouse", "Accesorios", 80000, 32000),
    ("Audífonos", "Accesorios", 180000, 81000),
    ("Webcam", "Accesorios", 200000, 100000),
], columns=["producto", "categoria", "precio_unitario", "costo_unitario"])
registros = []
for fecha in pd.date_range("2024-11-01", "2026-10-31"):
    mes = (fecha.year - 2024) * 12 + fecha.month - 11
    for canal in ["Tienda", "Web"]:
        # En Web crecen las operaciones y aumentan las rebajas durante el período.
        estacionalidad = 1.3 if fecha.month in [11, 12] else 1.0
        cantidad = int(rng.poisson((4 + mes * (0.22 if canal == "Web" else 0.07)) * estacionalidad))
        for _ in range(cantidad):
            producto = catalogo.iloc[int(rng.integers(len(catalogo)))]
            descuento = int(rng.choice([0, 5, 10]))
            if canal == "Web":
                descuento += min(mes // 4, 5)
            registros.append({
                "fecha": fecha, "canal": canal,
                **producto.to_dict(), "unidades": int(rng.integers(1, 4)),
                "descuento_pct": descuento
            })
ventas = pd.DataFrame(registros)
ventas.insert(0, "venta_id", [f"V{i:05d}" for i in range(1, len(ventas) + 1)])

ventas["venta_neta"] = ventas["unidades"] * ventas["precio_unitario"] * (1 - ventas["descuento_pct"] / 100)
ventas["cogs"] = ventas["unidades"] * ventas["costo_unitario"]
ventas["utilidad_bruta"] = ventas["venta_neta"] - ventas["cogs"]
ventas["mes"] = ventas["fecha"].dt.to_period("M").dt.to_timestamp()
MESES = pd.date_range(ventas["mes"].min(), ventas["mes"].max(), freq="MS")
CANALES = ["Todos", "Tienda", "Web"]
PERIODO = "Noviembre 2024–octubre 2026"

mensual_canal = ventas.groupby(["mes", "canal"], as_index=False)[["venta_neta", "utilidad_bruta"]].sum()
mensual_canal["margen_pct"] = 100 * mensual_canal["utilidad_bruta"] / mensual_canal["venta_neta"]

def filtrar(datos, canal="Todos", inicio=None, fin=None):
    seleccion = datos.copy()
    if canal != "Todos":
        seleccion = seleccion.loc[seleccion["canal"].eq(canal)]
    if inicio is not None:
        seleccion = seleccion.loc[seleccion["fecha"] >= pd.Timestamp(inicio)]
    if fin is not None:
        limite = pd.Timestamp(fin) + pd.offsets.MonthBegin(1)
        seleccion = seleccion.loc[seleccion["fecha"] < limite]
    return seleccion.copy()

def resumir(datos, meses=None):
    if meses is None:
        meses = MESES
    ingresos = datos["venta_neta"].sum()
    utilidad = datos["utilidad_bruta"].sum()
    margen = 100 * utilidad / ingresos if ingresos > 0 else None
    mensual = datos.groupby("mes")[["venta_neta", "utilidad_bruta"]].sum().reindex(meses, fill_value=0)
    # Un mes sin ventas tiene margen indefinido, no margen cero.
    mensual["margen_pct"] = mensual["utilidad_bruta"].div(mensual["venta_neta"].replace(0, np.nan)).mul(100)
    productos = datos.groupby("producto")["venta_neta"].sum().sort_values(ascending=False).head(5)
    return {"ingresos": ingresos, "utilidad": utilidad, "margen": margen,
            "registros": len(datos), "mensual": mensual, "productos": productos}

def construir_dashboard(datos, etiqueta="Todo el catálogo", meses=None):
    if meses is None:
        meses = MESES
    periodo = f"{meses[0]:%Y-%m} a {meses[-1]:%Y-%m}"
    if datos.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sin datos para esta selección", showarrow=False)
        fig.update_layout(template="plotly_white", title=etiqueta,
                          xaxis_visible=False, yaxis_visible=False)
        return fig

    r = resumir(datos, meses)
    # Millones en las tarjetas; COP completos disponibles en tablas y hover.
    indicadores = [
        ("Ventas netas · millones COP", r["ingresos"] / 1e6, ".1f", ""),
        ("Utilidad bruta · millones COP", r["utilidad"] / 1e6, ".1f", ""),
        ("Margen bruto", r["margen"], ".1f", "%"),
        ("Ventas registradas", r["registros"], ",.0f", "")
    ]

    graficos = []
    for col, (titulo, valor, formato, sufijo) in enumerate(indicadores, 1):
        graficos.append(go.Figure(go.Indicator(
            mode="number", value=valor,
            title={"text": titulo, "font": {"size": 13}},
            number={"valueformat": formato, "suffix": sufijo, "font": {"size": 31}})))
    m = r["mensual"]
    fig_ventas = px.line(
        m,
        x=m.index,
        y="venta_neta",
        markers=True,
        title="Ventas por mes",
        color_discrete_sequence=["#007F5F"],
        labels={"x": "Mes", "venta_neta": "Ventas netas (COP)"},
    )
    fig_ventas.update_traces(
        line_width=3,
        name="Ventas netas",
        hovertemplate="%{x|%Y-%m}<br>Ventas: %{y:,.0f} COP<extra></extra>",
    )
    graficos.append(fig_ventas)

    fig_margen = px.line(
        m,
        x=m.index,
        y="margen_pct",
        markers=True,
        title="Margen bruto por mes",
        color_discrete_sequence=["#8052A3"],
        labels={"x": "Mes", "margen_pct": "Margen (%)"},
    )
    fig_margen.update_traces(
        line_width=3,
        name="Margen bruto",
        hovertemplate="%{x|%Y-%m}<br>Margen: %{y:.2f}%<extra></extra>",
    )
    graficos.append(fig_margen)

    productos = r["productos"].sort_values()
    fig_ventas_producto = px.bar(
        productos,
        x='venta_neta',
        y=productos.index,
        title="Cinco productos con mayores ventas",
        color_discrete_sequence=["#1677A5"],
        labels={"venta_neta": "Ventas Netas (COP)", 'y': 'Producto'},
    )
    fig_ventas_producto.update_traces(
        name="Ventas por producto",
        hovertemplate="%{y}<br>Ventas: %{x:,.0f} COP<extra></extra>",
    )
    graficos.append(fig_ventas_producto)


    max_ventas = ventas.groupby("mes")["venta_neta"].sum().max()
    max_producto = ventas.groupby("producto")["venta_neta"].sum().max()
    graficos.append(f"Conecta | {etiqueta} {periodo} · Datos simulados · Valores sin IVA")
    return graficos

app.layout = html.Div(children=[
    html.H1(children='Dashboard Ventas'),
    html.Br(),
    html.Hr(),
    dcc.Dropdown(CANALES, 'Todos', id='dropdown-canales'),
    html.Br(),
    html.Div(children=[
      dcc.RangeSlider(
          min=0,
          max=len(MESES) - 1,
          value=(0, len(MESES) - 1),
          marks={
            index: mes.strftime("%Y-%m") for index, mes in enumerate(MESES)
          },
          allow_direct_input=False,
          id='slider-rango'
      )
    ]),
    html.Hr(),
    html.H3(id='titulo', style={ 'text-align': 'center' }),
    html.Div(children=[
      dcc.Graph(id='ventas-netas', style={ 'width': '25%'}),
      dcc.Graph(id='utilidad-bruta', style={ 'width': '25%'}),
      dcc.Graph(id='margen-bruto', style={ 'width': '25%'}),
      dcc.Graph(id='ventas-registradas', style={ 'width': '25%'}),
    ], style={ 'display':'flex', 'flex-direction': 'row', 'height': '100px', 'justify-content': 'space-around'}),
    html.Div(children=[
        dcc.Graph(id='ventas-mes'),
        dcc.Graph(id='margen-bruto-pct'),
    ], style={ 'display':'flex', 'flex-direction': 'row', 'justify-content': 'space-around'}),
    html.Div(children=[
        dcc.Graph(id='ventas-por-producto')
    ])
])

@callback(
  Output('ventas-netas', 'figure'),
  Output('utilidad-bruta', 'figure'),
  Output('margen-bruto', 'figure'),
  Output('ventas-registradas', 'figure'),
  Output('ventas-mes', 'figure'),
  Output('margen-bruto-pct', 'figure'),
  Output('ventas-por-producto', 'figure'),
  Output('titulo', 'children'),

  Input('dropdown-canales', 'value'),
  Input('slider-rango', 'value')
)
def actualizar_vista(canal, rango):
    index_inicio, index_fin = rango
    inicio = MESES[index_inicio]
    fin = MESES[index_fin]
    seleccion = filtrar(ventas, canal, inicio, fin)
    meses = pd.date_range(inicio, fin, freq="MS")
    print(f"Canal: {canal} | Desde {inicio:%Y-%m} hasta {fin:%Y-%m}, ambos incluidos")
    if seleccion.empty:
        print("No hay ventas en esta selección.")
        return
    return construir_dashboard(seleccion, f"Canal: {canal}", meses)


if __name__ == '__main__':
  app.run(debug=True)
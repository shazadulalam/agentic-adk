import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

df = pd.read_csv("datasets/bq-results-covid-open-data.csv")
fig = px.histogram(df, x=df.columns[0])

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("DataAngent Dashboard"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)

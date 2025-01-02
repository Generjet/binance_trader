import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import sqlite3
import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import sqlite3
import pandas as pd

app = dash.Dash(__name__)

PAGE_SIZE = 20

app.layout = html.Div([
    dcc.Graph(id='candlestick-chart'),
    dash_table.DataTable(
        id='table-data',
        columns=[{"name": i, "id": i} for i in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']],  # Explicitly define columns
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom'
    ),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
])

@app.callback(
    [Output('candlestick-chart', 'figure'), Output('table-data', 'data')],
    [Input('interval-component', 'n_intervals'), Input('table-data', 'page_current'), Input('table-data', 'page_size')]
)
def update_graph(n, page_current, page_size):
    conn = sqlite3.connect('tamir_crypto_data.db')
    df = pd.read_sql_query("SELECT * FROM crypto_data", conn)  # Read from crypto_data table
    conn.close()

    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(xaxis_rangeslider_visible=False)

    data = df.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')
    return fig, data


if __name__ == '__main__':
    app.run_server(debug=True)

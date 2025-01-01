import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import sqlite3
import pandas as pd
import time

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='candlestick-chart'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0) # Update every 1 second
])

@app.callback(
    Output('candlestick-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    conn = sqlite3.connect('tamir_crypto_data.db')
    dfs = []
    for table_name in pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist():
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df['Table'] = table_name  # Add a column to identify the table
        dfs.append(df)
    conn.close()

    combined_df = pd.concat(dfs, ignore_index=True)

    fig = go.Figure(data=[go.Candlestick(
        x=combined_df['Date'],
        open=combined_df['Open'],
        high=combined_df['High'],
        low=combined_df['Low'],
        close=combined_df['Close'],
        name=combined_df['Table']
    )])

    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

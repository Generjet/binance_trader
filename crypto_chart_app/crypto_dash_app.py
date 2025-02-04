import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from sqlalchemy import create_engine
import time

# Database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tamir4578',
    'database': 'portalblog_dev'
}

table_name = 'analyzed_data'
timestamp_col = 'time'
open_col = 'open'
high_col = 'high'
low_col = 'low'
close_col = 'close'

# Create database connection string
db_connection_str = 'mysql+pymysql://{user}:{password}@{host}/{database}'.format(**db_config)
db_connection = create_engine(db_connection_str)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=2*1000, # in milliseconds
        n_intervals=0
    ),
    dcc.Graph(id='candlestick-chart'),
    dcc.Graph(id='macd-chart'),
    dcc.Graph(id='rsi-chart'),
    dcc.Graph(id='stochastic-chart'),
])

def fetch_data_from_db():
    df = pd.read_sql_table(table_name, db_connection)
    df = df.sort_values(by=timestamp_col) # Ensure data is sorted by timestamp
    return df

def create_candlestick_chart(df):
    candlestick = go.Candlestick(
        x=df[timestamp_col],
        open=df[open_col],
        high=df[high_col],
        low=df[low_col],
        close=df[close_col]
    )

    layout = go.Layout(
        title='Candlestick Chart',
        xaxis=dict(title='Time'),
        yaxis=dict(title='Price')
    )

    fig = go.Figure(data=[candlestick], layout=layout)
    return fig

def create_macd_chart(df):
    macd_line = go.Scatter(
        x=df[timestamp_col],
        y=df['macd'], # Assuming 'macd' column exists
        name='MACD Line'
    )
    signal_line = go.Scatter(
        x=df[timestamp_col],
        y=df['ema'], # Assuming 'ema' is used as signal line, or replace with actual signal line column
        name='Signal Line'
    )
    layout = go.Layout(
        title='MACD',
        xaxis=dict(title='Time'),
        yaxis=dict(title='MACD Value')
    )
    fig = go.Figure(data=[macd_line, signal_line], layout=layout)
    return fig

def create_rsi_chart(df):
    rsi_line = go.Scatter(
        x=df[timestamp_col],
        y=df['rsi'], # Assuming 'rsi' column exists
        name='RSI'
    )
    layout = go.Layout(
        title='RSI',
        xaxis=dict(title='Time'),
        yaxis=dict(title='RSI Value'),
        yaxis_range=[0, 100]
    )
    fig = go.Figure(data=[rsi_line], layout=layout)
    return fig

def create_stochastic_chart(df):
    stochastic_k = go.Scatter(
        x=df[timestamp_col],
        y=df['stochastic_K'], # Assuming 'stochastic_K' column exists
        name='%K'
    )
    stochastic_d = go.Scatter(
        x=df[timestamp_col],
        y=df['stochastic_D'], # Assuming 'stochastic_D' column exists
        name='%D'
    )
    layout = go.Layout(
        title='Stochastic Oscillator',
        xaxis=dict(title='Time'),
        yaxis=dict(title='Stochastic Value'),
        yaxis_range=[0, 100]
    )
    fig = go.Figure(data=[stochastic_k, stochastic_d], layout=layout)
    return fig


@app.callback(
    [dash.dependencies.Output('candlestick-chart', 'figure'),
     dash.dependencies.Output('macd-chart', 'figure'),
     dash.dependencies.Output('rsi-chart', 'figure'),
     dash.dependencies.Output('stochastic-chart', 'figure')],
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_charts(n):
    df = fetch_data_from_db()
    candlestick_fig = create_candlestick_chart(df)
    macd_fig = create_macd_chart(df)
    rsi_fig = create_rsi_chart(df)
    stochastic_fig = create_stochastic_chart(df)
    return candlestick_fig, macd_fig, rsi_fig, stochastic_fig

if __name__ == '__main__':
    app.run_server(debug=True)
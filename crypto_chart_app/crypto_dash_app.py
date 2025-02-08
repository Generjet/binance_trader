import dash
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
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
        close=df[close_col],
        name='Candlestick'
    )

    ema_line = go.Scatter(
        x=df[timestamp_col],
        y=df['ema'], # Assuming 'ema' column exists
        name='EMA',
        line=dict(color='blue')
    )

    support_line = go.Scatter(
        x=df[timestamp_col],
        y=df['support'], # Assuming 'support' column exists
        name='Support',
        line=dict(color='green', dash='dash')
    )

    resistance_line = go.Scatter(
        x=df[timestamp_col],
        y=df['resistance'], # Assuming 'resistance' column exists
        name='Resistance',
        line=dict(color='red', dash='dash')
    )

    near_support_points = go.Scatter(
        x=df[timestamp_col],
        y=df['near_support'], # Assuming 'near_support' column exists
        mode='markers',
        marker=dict(color='green', symbol='circle', size=5),
        name='Near Support'
    )

    near_resistance_points = go.Scatter(
        x=df[timestamp_col],
        y=df['near_resistance'], # Assuming 'near_resistance' column exists
        mode='markers',
        marker=dict(color='red', symbol='circle', size=5),
        name='Near Resistance'
    )

    # Shift x-axis to the right to show last 300 candles clearly
    if len(df) > 300:
        x_range = [df[timestamp_col].iloc[-300], df[timestamp_col].iloc[-1]]
    else:
        x_range = [df[timestamp_col].iloc[0], df[timestamp_col].iloc[-1]]


    layout = go.Layout(
        title='Candlestick Chart with EMA, Support and Resistance',
        xaxis=dict(title='Time',
                   range=x_range), # Set x-axis range
        yaxis=dict(title='Price')
    )

    fig = go.Figure(data=[candlestick, ema_line, support_line, resistance_line, near_support_points, near_resistance_points], layout=layout)
    return fig

def create_macd_chart(df):
    macd_line = go.Scatter(
        x=df[timestamp_col],
        y=df['macd'], # Assuming 'macd' column exists
        name='MACD Line',
        marker_color='blue'
    )
    signal_line = go.Scatter(
        x=df[timestamp_col],
        y=df['macd_signal'], # Assuming 'macd_signal' column exists
        name='Signal Line',
        marker_color='red'
    )
    hist = go.Bar(
        x=df[timestamp_col],
        y=df['macd_hist'], # Assuming 'macd_hist' column exists
        name='Histogram',
        marker_color='grey'
    )
    layout = go.Layout(
        title='MACD',
        xaxis=dict(title='Time', showticklabels=False), # Hide x-axis labels
        yaxis=dict(title='MACD Value')
    )
    fig = go.Figure(data=[macd_line, signal_line, hist], layout=layout)
    return fig

def create_rsi_chart(df):
    rsi_line = go.Scatter(
        x=df[timestamp_col],
        y=df['rsi'], # Assuming 'rsi' column exists
        name='RSI'
    )
    layout = go.Layout(
        title='RSI',
        xaxis=dict(title='Time', showticklabels=False), # Hide x-axis labels
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
        xaxis=dict(title='Time', showticklabels=False), # Hide x-axis labels
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
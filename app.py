import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import sqlite3
import pandas as pd
import ta
import numpy as np

app = dash.Dash(__name__)

PAGE_SIZE = 20

app.layout = html.Div([
    dcc.Graph(id='candlestick-chart'),
    dash_table.DataTable(
        id='table-data',
        columns=[{"name": i, "id": i} for i in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'channel_trade']],  # Explicitly define columns
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom'
    ),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
])

def calculate_bollinger_bands(df, window=20, num_std_dev=2):
    df['BB_Middle'] = df['Close'].rolling(window=window).mean()
    df['BB_Std'] = df['Close'].rolling(window=window).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * num_std_dev)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * num_std_dev)
    return df


def generate_trade_signals(df):
    df['channel_trade'] = 'wait'
    # Example: Buy if RSI < 30, Sell if RSI > 70
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df.loc[df['RSI'] < 30, 'channel_trade'] = 'buy'
    df.loc[df['RSI'] > 70, 'channel_trade'] = 'sell'
    return df
@app.callback(
    [Output('candlestick-chart', 'figure'), Output('table-data', 'data')],
    [Input('interval-component', 'n_intervals'), Input('table-data', 'page_current'), Input('table-data', 'page_size')]
)
def update_graph(n, page_current, page_size):
    conn = sqlite3.connect('tamir_crypto_data.db')
    df = pd.read_sql_query("SELECT * FROM crypto_data", conn)  # Read from crypto_data table
    conn.close()

    # Calculate Bollinger Bands
    df = calculate_bollinger_bands(df)

    # Generate trade signals
    df = generate_trade_signals(df)

    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'
    )])

    # Add Bollinger Bands
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_Upper'], line=dict(color='purple', width=1), name='BB Upper'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_Lower'], line=dict(color='purple', width=1), name='BB Lower'))

    # Add trade signals
    trade_buy = df[df['channel_trade'] == 'buy']
    trade_sell = df[df['channel_trade'] == 'sell']
    fig.add_trace(go.Scatter(x=trade_buy['Date'], y=trade_buy['Close'], mode='markers', marker=dict(color='green', symbol='star', size=15), name='Buy'))
    fig.add_trace(go.Scatter(x=trade_sell['Date'], y=trade_sell['Close'], mode='markers', marker=dict(color='red', symbol='star', size=15), name='Sell'))

    fig.update_layout(xaxis_rangeslider_visible=False)

    data = df.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')
    return fig, data


if __name__ == '__main__':
    app.run_server(debug=True)

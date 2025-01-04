# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from binance.client import Client
import ta
import os
import sys
import time
from dash.dependencies import Input, Output, State

# GENERJET BINANCE ==>
# GENERJET API KEY and SECRET
api_key = os.getenv('binance_key')
api_secret = os.getenv('binance_secret')
client = Client(api_key, api_secret)
# ======== setting overall signal values to variables ====
currency = 'ETHUSDT'

# fetch new data
# ====== get data function ======
def fetchCryptoData(symbol, timePeriod, lookback, ago='days ago UTC'):
    lookback_str = str(lookback) + ' ' + ago
    df = pd.DataFrame(client.get_historical_klines(symbol, timePeriod, lookback_str))
    df = df.iloc[:,:6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index('Time', inplace=True)
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    print("fetch data ===>",df.tail(11))
    return df

# sqlite-aas data unshina
DB_NAME = '../tamir_crypto_data.db'
conn = sqlite3.connect(DB_NAME)

# Create table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS crypto_data (
    Time DATETIME PRIMARY KEY,
    Open REAL,
    High REAL,
    Low REAL,
    Close REAL,
    Volume REAL
);
"""
conn.execute(create_table_query)
conn.commit()

# Create table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS analyzed_1h (
    Time DATETIME PRIMARY KEY,
    Open REAL,
    High REAL,
    Low REAL,
    Close REAL,
    Volume REAL,
    resistance REAL,
    K REAL,
    D REAL,
    rsi REAL,
    macd REAL,
    ema REAL
);
"""
conn.execute(create_table_query)
conn.commit()

# Try to read existing data
try:
    query = "SELECT * FROM crypto_data ORDER BY Time DESC LIMIT 100"
    df = pd.read_sql_query(query, conn)
except pd.errors.DatabaseError:
    # If table is empty or error occurs, create empty DataFrame
    df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

conn.close()

# Create empty DataFrame
analyzed_df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

# Function to iterate over 'df' and append to 'analyzed_df'
def iterator_df(symbol='ETHUSDT', timePeriod='1h', lookback='30', ago='days ago UTC'):
    df = fetchCryptoData(symbol, timePeriod, lookback, ago)
    # global analyzed_df
    for index, row in df.iterrows():
        # row_df = pd.DataFrame([row]).dropna/(how='all')
        # if not row_df.empty:
        #     analyzed_df = pd.concat([analyzed_df, row_df], ignore_index=True)
        analyzed_df = analyzed_df.append(row)
        time.sleep(1)
    # technical analysis
    analyzed_df = find_extremum(analyzed_df)
    analyzed_df = applytechnicals(analyzed_df)
    print('ANALYZED DF ===>', analyzed_df)
    return analyzed_df

# =========== extremum ===============
def find_extremum(df):
    # Ensure 'High' column is numeric
    # df['High'] = pd.to_numeric(df['High'])

    # Find the last 2 maximum points of 'High'
    max_points = df['High'].nlargest(2)
    if len(max_points) < 2:
        df['resistance'] = None
        return df

    # Calculate the slope
    slope = (max_points.iloc[1] - max_points.iloc[0]) / (max_points.index[1] - max_points.index[0]).days

    # Calculate the next values for 'Resistance'
    df['resistance'] = max_points.iloc[1] + slope * (df.index - max_points.index[1]).days
    print("extremums = ", df.tail(10))
    return df

 # =========== TA technical analysis ===============
def applytechnicals(df):
    # Ensure columns are numeric
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    # Calculate technical indicators
    df['K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
    df['D'] = df['K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    df['macd'] = ta.trend.macd_diff(df['Close'])
    df['ema'] = df['Close'].ewm(span=14, adjust=False).mean()
    # Drop any rows with NaN values
    df.dropna(inplace=True)
    print("technicals => ",df.tail(10))
    return df
# Initialize the app ============ VIZUALIZE ============
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
]
app = Dash(__name__, assets_folder='assets', external_stylesheets=external_stylesheets)

# Save or update to 'analyzed_1h' table
def save_to_db(df):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO analyzed_1h (Time, Open, High, Low, Close, Volume, resistance, K, D, rsi, macd, ema)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['Time'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], row['resistance'], row['K'], row['D'], row['rsi'], row['macd'], row['ema']))
    conn.commit()
    conn.close()

# Function to get table names from the database
def get_table_names():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]

# Function to read data from the selected table
def read_table_data(table_name):
    conn = sqlite3.connect(DB_NAME)
    query = f"SELECT * FROM {table_name} ORDER BY Time DESC LIMIT 100"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Callback to update data and graphs
@app.callback(
    [Output('table', 'data'),
     Output('candlestick-graph', 'figure'),
     Output('stochastic-graph', 'figure'),
     Output('macd-graph', 'figure'),
     Output('rsi-graph', 'figure'),
     Output('ema-graph', 'figure')],
    [Input('execute-button', 'n_clicks')],
    [State('symbol-input', 'value'),
     State('timePeriod-input', 'value'),
     State('lookback-input', 'value'),
     State('table-select', 'value')]
)
def update_data(n_clicks, symbol, timePeriod, lookback, table_name):
    if n_clicks is None:
        raise PreventUpdate

    global analyzed_df
    analyzed_df = iterator_df(symbol, timePeriod, lookback)
    save_to_db(analyzed_df)
    # if table_name:
    #     analyzed_df = read_table_data(table_name)
    # else:
    #     analyzed_df = iterator_df(symbol, timePeriod, lookback)
    #     save_to_db(analyzed_df)

    # Create candlestick chart with dark theme
    fig_candlestick = go.Figure(data=[go.Candlestick(
        x=analyzed_df.index,
        open=analyzed_df['Open'],
        high=analyzed_df['High'],
        low=analyzed_df['Low'],
        close=analyzed_df['Close']
    )])
    fig_candlestick.update_layout(template='plotly_dark')

    # Create Stochastic Oscillator chart
    fig_stochastic = go.Figure()
    fig_stochastic.add_trace(go.Scatter(x=analyzed_df.index, y=analyzed_df['K'], mode='lines', name='%K'))
    fig_stochastic.add_trace(go.Scatter(x=analyzed_df.index, y=analyzed_df['D'], mode='lines', name='%D'))
    fig_stochastic.update_layout(template='plotly_dark', title='Stochastic Oscillator')

    # Create MACD chart with Volume
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=analyzed_df.index, y=analyzed_df['macd'], mode='lines', name='MACD'))
    fig_macd.add_trace(go.Bar(x=analyzed_df.index, y=analyzed_df['Volume'], name='Volume', yaxis='y2'))
    fig_macd.update_layout(
        template='plotly_dark',
        title='MACD with Volume',
        yaxis=dict(title='MACD'),
        yaxis2=dict(title='Volume', overlaying='y', side='right')
    )

    # Create RSI chart
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=analyzed_df.index, y=analyzed_df['rsi'], mode='lines', name='RSI'))
    fig_rsi.update_layout(template='plotly_dark', title='RSI')

    # Create EMA chart
    fig_ema = go.Figure()
    fig_ema.add_trace(go.Scatter(x=analyzed_df.index, y=analyzed_df['ema'], mode='lines', name='EMA'))
    fig_ema.update_layout(template='plotly_dark', title='EMA')

    return analyzed_df.to_dict('records'), fig_candlestick, fig_stochastic, fig_macd, fig_rsi, fig_ema

# App layout
app.layout = html.Div(children=[
    html.Div(className='header', children=[
        html.I(className='fa fa-bitcoin'),
        html.Span(' Crypto Trading System')
    ]),
    html.Div(children=[
        dcc.Input(id='symbol-input', type='text', placeholder='Symbol', value='ETHUSDT', style={'marginRight': '10px'}),
        dcc.Input(id='timePeriod-input', type='text', placeholder='Time Period', value='1h', style={'marginRight': '10px'}),
        dcc.Input(id='lookback-input', type='number', placeholder='Lookback', value=200, style={'marginRight': '10px'}),
        dcc.Dropdown(
            id='table-select',
            options=[{'label': table, 'value': table} for table in get_table_names()],
            placeholder='Select Table',
            style={'marginRight': '10px', 'width': '200px'}
        ),
        html.Button('Execute', id='execute-button', n_clicks=0)
    ], style={'padding': '20px'}),
    dash_table.DataTable(
        id='table',
        data=analyzed_df.to_dict('records'),
        page_size=10,
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_header={'backgroundColor': '#333333', 'color': 'green'},
        style_cell={'backgroundColor': '#1e1e1e', 'color': 'grey'}
    ),
    dcc.Graph(id='candlestick-graph'),
    dcc.Graph(id='stochastic-graph'),
    dcc.Graph(id='macd-graph'),
    dcc.Graph(id='rsi-graph'),
    dcc.Graph(id='ema-graph'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

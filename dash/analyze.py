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

# GENERJET BINANCE ==>
# GENERJET API KEY and SECRET
api_key = os.getenv('binance_key')
api_secret = os.getenv('binance_secret')
client = Client(api_key, api_secret)
# ======== setting overall signal values to variables ====
currency = 'ETHUSDT'

# fetch new data
# ====== get data function ======
def fetchCryptoData(symbol, timePeriod ,lookback, ago='days ago UTC'):
    df = pd.DataFrame(client.get_historical_klines(symbol, timePeriod, lookback + ago ))
    df = df.iloc[:,:6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    # df['Time'] = pd.to_datetime(df['Time'], unit='ms').dt.strftime('%Y-%m-D %H:%M')
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index('Time', inplace=True)
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    # print(df.tail(10))
    return df

# sqlite-aas data unshina
# DB_NAME = '../tamir_crypto_data.db'
# conn = sqlite3.connect(DB_NAME)

# # Create table if it doesn't exist
# create_table_query = """
# CREATE TABLE IF NOT EXISTS crypto_data (
#     Time DATETIME PRIMARY KEY,
#     Open REAL,
#     High REAL,
#     Low REAL,
#     Close REAL,
#     Volume REAL
# );
# """
# conn.execute(create_table_query)
# conn.commit()

# # Try to read existing data
# try:
#     query = "SELECT * FROM crypto_data ORDER BY Time DESC LIMIT 100"
#     df = pd.read_sql_query(query, conn)
# except pd.errors.DatabaseError:
#     # If table is empty or error occurs, create empty DataFrame
#     df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

# conn.close()

# get new data
symbol = 'ETHUSDT'
timePeriod = '4h'
lookback = '200'
df = fetchCryptoData(symbol, timePeriod, lookback )

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

df = find_extremum(df)
df = applytechnicals(df)
print(df.tail(10))

# Convert columns to numeric
df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].apply(pd.to_numeric)

# Create candlestick chart with dark theme
fig_candlestick = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])
fig_candlestick.update_layout(template='plotly_dark')

# Create Stochastic Oscillator chart
fig_stochastic = go.Figure()
fig_stochastic.add_trace(go.Scatter(x=df.index, y=df['K'], mode='lines', name='%K'))
fig_stochastic.add_trace(go.Scatter(x=df.index, y=df['D'], mode='lines', name='%D'))
fig_stochastic.update_layout(template='plotly_dark', title='Stochastic Oscillator')

# Create MACD chart with Volume
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=df.index, y=df['macd'], mode='lines', name='MACD'))
fig_macd.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', yaxis='y2'))
fig_macd.update_layout(
    template='plotly_dark',
    title='MACD with Volume',
    yaxis=dict(title='MACD'),
    yaxis2=dict(title='Volume', overlaying='y', side='right')
)

# Create RSI chart
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df.index, y=df['rsi'], mode='lines', name='RSI'))
fig_rsi.update_layout(template='plotly_dark', title='RSI')

# Create EMA chart
fig_ema = go.Figure()
fig_ema.add_trace(go.Scatter(x=df.index, y=df['ema'], mode='lines', name='EMA'))
fig_ema.update_layout(template='plotly_dark', title='EMA')

# App layout
app.layout = html.Div(children=[
    html.Div(className='header', children=[
        html.I(className='fa fa-bitcoin'),
        html.Span(' Crypto Trading System')
    ]),
    dash_table.DataTable(
        data=df.to_dict('records'),
        page_size=10
    ),
    dcc.Graph(figure=fig_candlestick),
    dcc.Graph(figure=fig_stochastic),
    dcc.Graph(figure=fig_macd),
    dcc.Graph(figure=fig_rsi),
    dcc.Graph(figure=fig_ema),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
